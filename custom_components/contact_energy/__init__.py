"""Contact Energy integration for Home Assistant."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

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

    def __init__(self, hass: HomeAssistant, api: ContactEnergyApi, config_data: dict) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api
        self.usage_days = config_data.get("usage_days", 10)

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