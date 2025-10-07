"""Contact Energy integration for Home Assistant."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

import asyncio
from .api import ContactEnergyApi
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Contact Energy from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create API instance
    api = ContactEnergyApi(
        hass,
        entry.data["email"],
        entry.data["password"],
        entry.data.get("account_id"),
        entry.data.get("contract_id")
    )

    # Create coordinator
    coordinator = ContactEnergyCoordinator(hass, api, entry.data)

    # Perform initial data fetch
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class ContactEnergyCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Contact Energy data."""

    def __init__(self, hass: HomeAssistant, api: ContactEnergyApi, config_data: dict, entry: ConfigEntry = None) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api
        self.usage_days = config_data.get("usage_days", 10)
        self.entry = entry
        from .const import CONF_AUTO_RESTART_ENABLED, CONF_AUTO_RESTART_TIME, DEFAULT_AUTO_RESTART_ENABLED, DEFAULT_AUTO_RESTART_TIME
        self._reload_enabled = config_data.get(CONF_AUTO_RESTART_ENABLED, DEFAULT_AUTO_RESTART_ENABLED)
        self._reload_time = config_data.get(CONF_AUTO_RESTART_TIME, DEFAULT_AUTO_RESTART_TIME)
        self._reload_task = None
        if entry:
            entry.add_update_listener(self._handle_options_update)
        if self._reload_enabled:
            self._schedule_next_reload()

    def _calculate_next_reload(self):
        import homeassistant.util.dt as dt_util
        now = dt_util.now(self.hass.config.time_zone)
        hour, minute = map(int, self._reload_time.split(":"))
        next_reload = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_reload <= now:
            next_reload += timedelta(days=1)
        return next_reload

    def _schedule_next_reload(self):
        if self._reload_task:
            self._reload_task.cancel()
        next_reload = self._calculate_next_reload()
        delay = (next_reload - self.hass.util.dt.now()).total_seconds()
        _LOGGER.info("Next Contact Energy restart scheduled for: %s", next_reload.strftime("%Y-%m-%d %H:%M:%S %Z"))
        self._reload_task = self.hass.async_create_task(self._wait_and_reload(delay))

    async def _wait_and_reload(self, delay: float):
        try:
            await asyncio.sleep(delay)
            await self._perform_daily_reload()
        except asyncio.CancelledError:
            _LOGGER.debug("Restart task cancelled")
        except Exception as error:
            _LOGGER.exception("Unexpected error in restart task: %s", error)
        finally:
            if self._reload_enabled:
                self._schedule_next_reload()

    async def _perform_daily_reload(self):
        max_retries = 5
        retry_delay = 300
        for attempt in range(max_retries):
            try:
                await self.hass.config_entries.async_reload(self.entry.entry_id)
                _LOGGER.info("Contact Energy restart successful on attempt %d", attempt + 1)
                return
            except Exception as error:
                _LOGGER.warning("Restart attempt %d failed: %s", attempt + 1, error)
                if attempt < max_retries - 1:
                    _LOGGER.info("Retrying in 5 minutes...")
                    await asyncio.sleep(retry_delay)
                else:
                    await self._notify_reload_failure(str(error))

    async def _notify_reload_failure(self, error_msg: str):
        from homeassistant.components.persistent_notification import async_create
        await async_create(
            self.hass,
            f"Scheduled restart of Contact Energy integration failed: {error_msg}. You may need to manually reload the integration.",
            title="Contact Energy - Restart Failed",
            notification_id=f"{DOMAIN}_restart_failed"
        )

    async def _handle_options_update(self, hass, entry):
        old_enabled = self._reload_enabled
        old_time = self._reload_time
        from .const import CONF_AUTO_RESTART_ENABLED, CONF_AUTO_RESTART_TIME, DEFAULT_AUTO_RESTART_ENABLED, DEFAULT_AUTO_RESTART_TIME
        self._reload_enabled = entry.options.get(CONF_AUTO_RESTART_ENABLED, DEFAULT_AUTO_RESTART_ENABLED)
        self._reload_time = entry.options.get(CONF_AUTO_RESTART_TIME, DEFAULT_AUTO_RESTART_TIME)
        if old_enabled != self._reload_enabled or old_time != self._reload_time:
            if self._reload_task:
                self._reload_task.cancel()
            if self._reload_enabled:
                _LOGGER.info("Auto-restart rescheduled: enabled=%s, time=%s", self._reload_enabled, self._reload_time)
                self._schedule_next_reload()
            else:
                _LOGGER.info("Auto-restart disabled")

    async def _async_update_data(self) -> dict:
        """Fetch data from Contact Energy."""
        # Ensure we're logged in
        if not self.api._api_token and not await self.api.async_login():
            raise Exception("Failed to authenticate with Contact Energy")

        # Fetch account data
        account_data = await self.api.async_get_accounts()
        
        # Fetch usage data will be handled by the usage sensor directly
        # to avoid loading all historical data during every coordinator update
        
        return {
            "account": account_data,
            "last_update": self.last_update_success,
        }