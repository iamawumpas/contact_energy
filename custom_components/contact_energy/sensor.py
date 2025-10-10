# --- Entity setup function ---
async def async_setup_entry(
    hass: HomeAssistant, 
    entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Contact Energy sensor entities from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    icp = entry.data[CONF_CONTRACT_ICP]
    usage_days = entry.data.get(CONF_USAGE_DAYS, 10)

    sensors = [
        ContactEnergyUsageSensor(coordinator, api, icp, usage_days),
        ContactEnergyDailyConsumptionSensor(coordinator, api, icp, usage_days),
        ContactEnergyDailyFreeConsumptionSensor(coordinator, api, icp, usage_days),
        ContactEnergyAccountSensor(
            coordinator,
            icp,
            SENSOR_ACCOUNT_BALANCE_NAME,
            CURRENCY_DOLLAR,
            "mdi:cash",
            None,
            SensorDeviceClass.MONETARY,
            lambda data: data.get("accountDetail", {}).get("accountBalance", {}).get("currentBalance"),
        ),
        ContactEnergyAccountSensor(
            coordinator,
            icp,
            SENSOR_NEXT_BILL_AMOUNT_NAME,
            CURRENCY_DOLLAR,
            "mdi:cash-clock",
            None,
            SensorDeviceClass.MONETARY,
            lambda data: data.get("accountDetail", {}).get("nextBill", {}).get("amount"),
        ),
        ContactEnergyAccountSensor(
            coordinator,
            icp,
            SENSOR_NEXT_BILL_DATE_NAME,
            None,
            "mdi:calendar",
            None,
            SensorDeviceClass.DATE,
            lambda data: _parse_date(data.get("accountDetail", {}).get("nextBill", {}).get("date")),
        ),
        ContactEnergyAccountSensor(
            coordinator,
            icp,
            SENSOR_PAYMENT_DUE_NAME,
            CURRENCY_DOLLAR,
            "mdi:cash-marker",
            None,
            SensorDeviceClass.MONETARY,
            lambda data: data.get("accountDetail", {}).get("invoice", {}).get("amountDue"),
        ),
        ContactEnergyAccountSensor(
            coordinator,
            icp,
            SENSOR_PAYMENT_DUE_DATE_NAME,
            None,
            "mdi:calendar-clock",
            None,
            SensorDeviceClass.DATE,
            lambda data: _parse_date(data.get("accountDetail", {}).get("invoice", {}).get("paymentDueDate")),
        ),
        ContactEnergyAccountSensor(
            coordinator,
            icp,
            SENSOR_PREVIOUS_READING_DATE_NAME,
            None,
            "mdi:calendar",
            None,
            SensorDeviceClass.DATE,
            lambda data: _parse_meter_reading_date(data, "previousMeterReadingDate"),
        ),
        ContactEnergyAccountSensor(
            coordinator,
            icp,
            SENSOR_NEXT_READING_DATE_NAME,
            None,
            "mdi:calendar",
            None,
            SensorDeviceClass.DATE,
            lambda data: _parse_meter_reading_date(data, "nextMeterReadDate"),
        ),
    ]
    async_add_entities(sensors, True)
"""Contact Energy sensors - consolidated implementation."""

import asyncio
import logging
from homeassistant.helpers.storage import Store
from datetime import datetime, timedelta, date
from typing import Any, Callable, Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
from homeassistant.components.recorder.statistics import async_add_external_statistics
from homeassistant.const import (
    CURRENCY_DOLLAR,
    CONF_EMAIL,
    CONF_PASSWORD,
    UnitOfEnergy
)

from .const import (
    DOMAIN,
    NAME,
    CONF_USAGE_DAYS,
    CONF_ACCOUNT_ID,
    CONF_CONTRACT_ID,
    CONF_CONTRACT_ICP,
    SENSOR_USAGE_NAME,
    SENSOR_ACCOUNT_BALANCE_NAME,
    SENSOR_NEXT_BILL_AMOUNT_NAME,
    SENSOR_NEXT_BILL_DATE_NAME,
    SENSOR_PAYMENT_DUE_NAME,
    SENSOR_PAYMENT_DUE_DATE_NAME,
    SENSOR_PREVIOUS_READING_DATE_NAME,
    SENSOR_NEXT_READING_DATE_NAME
)

_LOGGER = logging.getLogger(__name__)



# ...existing code...

# Move async_setup_entry below all class definitions


# ...existing code...

# Move async_setup_entry to the end of the file
class ContactEnergyDailyConsumptionSensor(ContactEnergyBaseSensor):
    """Sensor for daily electricity consumption (kWh)."""
    def __init__(self, coordinator, api, icp: str, usage_days: int = 10):
        super().__init__(
            coordinator,
            icp,
            "Daily Consumption",
            UnitOfEnergy.KILO_WATT_HOUR,
            "mdi:meter-electric",
            SensorStateClass.MEASUREMENT,
            SensorDeviceClass.ENERGY,
        )
        self._api = api
        self._usage_days = usage_days
        self._state = 0
        self._last_date = None


    # Daily Consumption Sensor
    class ContactEnergyDailyConsumptionSensor(ContactEnergyBaseSensor):
        """Sensor for daily electricity consumption (kWh)."""
        def __init__(self, coordinator, api, icp: str, usage_days: int = 10):
            super().__init__(
                coordinator,
                icp,
                "Daily Consumption",
                UnitOfEnergy.KILO_WATT_HOUR,
                "mdi:meter-electric",
                SensorStateClass.MEASUREMENT,
                SensorDeviceClass.ENERGY,
            )
            self._api = api
            self._usage_days = usage_days
            self._state = 0
            self._last_date = None

        @property
        def native_value(self) -> float:
            return self._state

        async def async_update(self) -> None:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            response = await self._api.get_usage(str(today.year), str(today.month), str(today.day))
            daily_kwh = 0
            if response:
                for point in response:
                    offpeak_value_str = str(point.get("offpeakValue", "0.00"))
                    value_float = ContactEnergyUsageSensor._safe_float(point.get("value"))
                    if offpeak_value_str == "0.00":
                        daily_kwh += value_float
            self._state = daily_kwh
            self._last_date = today

    # Daily Free Consumption Sensor
    class ContactEnergyDailyFreeConsumptionSensor(ContactEnergyBaseSensor):
        """Sensor for daily free electricity consumption (kWh)."""
        def __init__(self, coordinator, api, icp: str, usage_days: int = 10):
            super().__init__(
                coordinator,
                icp,
                "Daily Free Consumption",
                UnitOfEnergy.KILO_WATT_HOUR,
                "mdi:meter-electric-outline",
                SensorStateClass.MEASUREMENT,
                SensorDeviceClass.ENERGY,
            )
            self._api = api
            self._usage_days = usage_days
            self._state = 0
            self._last_date = None

        @property
        def native_value(self) -> float:
            return self._state

        async def async_update(self) -> None:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            response = await self._api.get_usage(str(today.year), str(today.month), str(today.day))
            daily_free_kwh = 0
            if response:
                for point in response:
                    offpeak_value_str = str(point.get("offpeakValue", "0.00"))
                    value_float = ContactEnergyUsageSensor._safe_float(point.get("value"))
                    if offpeak_value_str != "0.00":
                        daily_free_kwh += value_float
            self._state = daily_free_kwh
            self._last_date = today
            lambda data: data.get("accountDetail", {}).get("nextBill", {}).get("amount"),
        ),
        ContactEnergyAccountSensor(
            coordinator,
            icp,
            SENSOR_NEXT_BILL_DATE_NAME,
            None,
            "mdi:calendar",
            None,
            SensorDeviceClass.DATE,
            lambda data: _parse_date(data.get("accountDetail", {}).get("nextBill", {}).get("date")),
        ),
        ContactEnergyAccountSensor(
            coordinator,
            icp,
            SENSOR_PAYMENT_DUE_NAME,
            CURRENCY_DOLLAR,
            "mdi:cash-marker",
            None,  # No state class for monetary sensors
            SensorDeviceClass.MONETARY,
            lambda data: data.get("accountDetail", {}).get("invoice", {}).get("amountDue"),
        ),
        ContactEnergyAccountSensor(
            coordinator,
            icp,
            SENSOR_PAYMENT_DUE_DATE_NAME,
            None,
            "mdi:calendar-clock",
            None,
            SensorDeviceClass.DATE,
            lambda data: _parse_date(data.get("accountDetail", {}).get("invoice", {}).get("paymentDueDate")),
        ),
        ContactEnergyAccountSensor(
            coordinator,
            icp,
            SENSOR_PREVIOUS_READING_DATE_NAME,
            None,
            "mdi:calendar",
            None,
            SensorDeviceClass.DATE,
            lambda data: _parse_meter_reading_date(data, "previousMeterReadingDate"),
        ),
        ContactEnergyAccountSensor(
            coordinator,
            icp,
    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data or "account" not in self.coordinator.data:
            return None
        
        try:
            return self._value_fn(self.coordinator.data["account"])
        except (KeyError, TypeError, AttributeError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        attrs = {}
        
        # Use last_update_success_time for datetime if available
        if hasattr(self.coordinator, 'last_update_success_time') and self.coordinator.last_update_success_time:
            attrs["last_updated"] = self.coordinator.last_update_success_time.isoformat()
        
        # Add payment history for monetary sensors
        if (self._attr_device_class == SensorDeviceClass.MONETARY and 
            self.coordinator.data and "account" in self.coordinator.data):
            account_data = self.coordinator.data["account"]
            payments = account_data.get("accountDetail", {}).get("payments", [])
            if payments:
                attrs["recent_payments"] = [
                    {"amount": p.get("amount"), "date": p.get("date")}
                    for p in payments[:5]  # Last 5 payments
                ]
        
        return attrs


class ContactEnergyUsageSensor(ContactEnergyBaseSensor):
    """Sensor for Contact Energy usage tracking with statistics."""

    def __init__(
        self,
        coordinator,
        api,
        icp: str,
        usage_days: int = 10,
    ) -> None:
        """Initialize the usage sensor."""
        super().__init__(
            coordinator,
            icp,
            SENSOR_USAGE_NAME,
            UnitOfEnergy.KILO_WATT_HOUR,
            "mdi:meter-electric",
            SensorStateClass.TOTAL,
            SensorDeviceClass.ENERGY,
        )
        self._api = api
        self._usage_days = usage_days
        self._state = 0
        self._last_usage_update = None
        self._initial_download_complete = False
        self._download_task = None
        self._download_progress = {"completed": 0, "total": usage_days, "errors": 0}
        self._stored_data = None  # Will hold cached statistics data
        self._storage_key = f"contact_energy_usage_{self._icp}"

    @property
    def native_value(self) -> float:
        """Return the current total usage."""
        return self._state

    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state."""
        return False

    async def async_added_to_hass(self) -> None:
        """Called when entity is added to Home Assistant."""
        await super().async_added_to_hass()
        
        # Load existing data from storage
        await self._load_stored_data()
        
        # Start background download for large datasets
        if self._usage_days > 30 and not self._initial_download_complete:
            _LOGGER.info(
                "Starting background download for %s days of usage data. "
                "This may take several minutes.", 
                self._usage_days
            )
            
            # Create notification for large downloads
            await self.hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "message": f"Contact Energy is downloading {self._usage_days} days of usage data in the background. "
                               f"This may take several minutes. You will be notified when complete.",
                    "title": "Contact Energy - Data Download Started",
                    "notification_id": f"{DOMAIN}_download_{self._icp}"
                }
            )
            
            # Start the background task
            self._download_task = self.hass.async_create_task(
                self._background_download_all_data()
            )
    
    async def async_will_remove_from_hass(self) -> None:
        """Called when entity is about to be removed from Home Assistant."""
        if self._download_task and not self._download_task.done():
            self._download_task.cancel()
            _LOGGER.debug("Cancelled background download task")
        await super().async_will_remove_from_hass()

    async def async_update(self) -> None:
        """Update usage data and statistics."""
        # For small datasets or after initial download, use normal update cycle
        if self._initial_download_complete or self._usage_days <= 30:
            now = datetime.now()
            if (self._last_usage_update and 
                (now - self._last_usage_update) < timedelta(hours=8)):
                return

            _LOGGER.debug("Updating usage data for %s days", self._usage_days)
            
            try:
                await self._update_usage_statistics()
                self._last_usage_update = now
            except Exception as error:
                _LOGGER.error("Failed to update usage statistics: %s", error)

    async def _update_usage_statistics(self) -> None:
        """Fetch recent usage data and update statistics incrementally."""
        if not self._api._api_token and not await self._api.async_login():
            _LOGGER.error("Failed to login for usage data")
            return

        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Determine how many days to fetch based on stored data
        days_to_fetch = 1  # Default: just fetch yesterday and today
        start_date = today - timedelta(days=1)
        
        if self._stored_data and "last_update" in self._stored_data:
            try:
                last_update = datetime.fromisoformat(self._stored_data["last_update"])
                days_since_update = (now - last_update).days
                # Fetch missing days plus a small buffer
                days_to_fetch = min(days_since_update + 2, 7)  # Max 7 days
                start_date = today - timedelta(days=days_to_fetch)
                _LOGGER.debug("Incremental update: fetching %s days since %s", 
                             days_to_fetch, last_update.date())
            except (ValueError, TypeError):
                _LOGGER.warning("Invalid last_update in stored data, fetching recent days")
        else:
            # No stored data, but don't fetch everything - just recent days
            days_to_fetch = min(self._usage_days, 30)  # Max 30 days for initial
            start_date = today - timedelta(days=days_to_fetch)
            _LOGGER.info("No stored data found, fetching recent %s days", days_to_fetch)

        # Load existing statistics from storage
        kwh_statistics = []
        dollar_statistics = []
        free_kwh_statistics = []
        kwh_running_sum = 0
        dollar_running_sum = 0
        free_kwh_running_sum = 0
        currency = 'NZD'
        
        if self._stored_data and "statistics" in self._stored_data:
            # Load existing data
            stored_stats = self._stored_data["statistics"]
            kwh_running_sum = stored_stats.get("kwh_total", 0)
            dollar_running_sum = stored_stats.get("dollar_total", 0)
            free_kwh_running_sum = stored_stats.get("free_kwh_total", 0)
            currency = stored_stats.get("currency", "NZD")

        # Fetch only recent days
        for i in range(days_to_fetch):
            current_date = start_date + timedelta(days=i)
            if current_date > today:
                break
                
            _LOGGER.debug("Fetching incremental usage data for %s", current_date.strftime("%Y-%m-%d"))
            
            response = await self._api.get_usage(
                str(current_date.year), 
                str(current_date.month), 
                str(current_date.day)
            )

            if not response:
                continue

            daily_kwh = 0
            daily_dollar = 0
            daily_free_kwh = 0

            for point in response:
                if point.get('currency') and currency != point['currency']:
                    currency = point['currency']

                # Safely convert values
                value_float = self._safe_float(point.get("value"))
                dollar_value_float = self._safe_float(point.get("dollarValue"))
                offpeak_value_str = str(point.get("offpeakValue", "0.00"))

                # If offpeak value is not '0.00', the energy is free
                if offpeak_value_str == "0.00":
                    daily_kwh += value_float
                    daily_dollar += dollar_value_float
                else:
                    daily_free_kwh += value_float

            # Update running totals
            kwh_running_sum += daily_kwh
            dollar_running_sum += daily_dollar
            free_kwh_running_sum += daily_free_kwh

            # Create statistics entries for this day
            if daily_kwh > 0 or daily_dollar > 0 or daily_free_kwh > 0:
                day_start = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
                kwh_statistics.append(StatisticData(start=day_start, sum=kwh_running_sum))
                dollar_statistics.append(StatisticData(start=day_start, sum=dollar_running_sum))
                if daily_free_kwh > 0:
                    free_kwh_statistics.append(StatisticData(start=day_start, sum=free_kwh_running_sum))

        # Limit statistics lists to the most recent 30 days
        MAX_STATS_DAYS = 30
        if kwh_statistics:
            kwh_statistics = kwh_statistics[-MAX_STATS_DAYS:]
            dollar_statistics = dollar_statistics[-MAX_STATS_DAYS:]
            free_kwh_statistics = free_kwh_statistics[-MAX_STATS_DAYS:]
            await self._add_statistics(kwh_statistics, dollar_statistics, free_kwh_statistics, currency)
            
        # Save updated totals to storage
        await self._save_stored_data(kwh_running_sum, {
            "kwh_total": kwh_running_sum,
            "dollar_total": dollar_running_sum, 
            "free_kwh_total": free_kwh_running_sum,
            "currency": currency
        })
        
        self._state = kwh_running_sum
        _LOGGER.info("Updated usage statistics: %.2f kWh total (incremental update)", kwh_running_sum)

    async def _background_download_all_data(self) -> None:
        """Download all historical data in the background with progress updates."""
        try:
            _LOGGER.info("Starting background download of %s days of usage data", self._usage_days)
            
            if not self._api._api_token and not await self._api.async_login():
                _LOGGER.error("Failed to login for background data download")
                await self._notify_download_error("Authentication failed")
                return

            now = datetime.now()
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)

            kwh_statistics = []
            kwh_running_sum = 0
            dollar_statistics = []
            dollar_running_sum = 0
            free_kwh_statistics = []
            free_kwh_running_sum = 0
            currency = 'NZD'
            
            # Process in chunks to avoid overwhelming the system
            chunk_size = 10
            total_chunks = (self._usage_days + chunk_size - 1) // chunk_size
            
            for chunk_num in range(total_chunks):
                chunk_start = chunk_num * chunk_size
                chunk_end = min(chunk_start + chunk_size, self._usage_days)
                
                _LOGGER.debug("Processing chunk %s/%s (days %s-%s)", 
                             chunk_num + 1, total_chunks, chunk_start, chunk_end)
                
                # Process this chunk
                for i in range(chunk_start, chunk_end):
                    current_date = today - timedelta(days=self._usage_days - i)
                    
                    try:
                        response = await self._api.get_usage(
                            str(current_date.year), 
                            str(current_date.month), 
                            str(current_date.day)
                        )

                        if response:
                            for point in response:
                                if point.get('currency') and currency != point['currency']:
                                    currency = point['currency']

                                # Safely convert values
                                value_float = self._safe_float(point.get("value"))
                                dollar_value_float = self._safe_float(point.get("dollarValue"))
                                offpeak_value_str = str(point.get("offpeakValue", "0.00"))

                                # If offpeak value is not '0.00', the energy is free
                                if offpeak_value_str == "0.00":
                                    kwh_running_sum += value_float
                                    dollar_running_sum += dollar_value_float
                                else:
                                    free_kwh_running_sum += value_float

                                # Parse date safely
                                try:
                                    date_obj = datetime.strptime(point["date"], "%Y-%m-%dT%H:%M:%S.%f%z")
                                except (ValueError, TypeError, KeyError):
                                    date_obj = current_date

                                # Add to statistics
                                kwh_statistics.append(StatisticData(start=date_obj, sum=kwh_running_sum))
                                dollar_statistics.append(StatisticData(start=date_obj, sum=dollar_running_sum))
                                free_kwh_statistics.append(StatisticData(start=date_obj, sum=free_kwh_running_sum))
                        
                        self._download_progress["completed"] += 1
                        
                    except Exception as error:
                        _LOGGER.warning("Failed to fetch data for %s: %s", 
                                      current_date.strftime("%Y-%m-%d"), error)
                        self._download_progress["errors"] += 1
                
                # Update progress notification every chunk
                progress_pct = int((chunk_end / self._usage_days) * 100)
                await self.hass.services.async_call(
                    "persistent_notification",
                    "create",
                    {
                        "message": f"Downloaded {chunk_end}/{self._usage_days} days ({progress_pct}%). "
                                   f"Errors: {self._download_progress['errors']}",
                        "title": "Contact Energy - Download Progress",
                        "notification_id": f"{DOMAIN}_download_{self._icp}"
                    }
                )
                
                # Add small delay between chunks to be nice to the API
                await asyncio.sleep(1)

            # Limit statistics lists to the most recent 30 days
            MAX_STATS_DAYS = 30
            kwh_statistics = kwh_statistics[-MAX_STATS_DAYS:]
            dollar_statistics = dollar_statistics[-MAX_STATS_DAYS:]
            free_kwh_statistics = free_kwh_statistics[-MAX_STATS_DAYS:]
            await self._add_statistics(kwh_statistics, dollar_statistics, free_kwh_statistics, currency)
            self._state = kwh_running_sum
            self._initial_download_complete = True
            self._last_usage_update = now

            # Success notification
            await self.hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "message": f"Successfully downloaded {self._download_progress['completed']} days of usage data. "
                               f"Errors: {self._download_progress['errors']}. Data is now available in the Energy Dashboard.",
                    "title": "Contact Energy - Download Complete",
                    "notification_id": f"{DOMAIN}_download_{self._icp}"
                }
            )
            
            _LOGGER.info("Background download completed successfully. Days: %s, Errors: %s", 
                        self._download_progress['completed'], self._download_progress['errors'])

        except Exception as error:
            _LOGGER.exception("Background download failed: %s", error)
            await self._notify_download_error(f"Download failed: {error}")

    async def _notify_download_error(self, error_msg: str) -> None:
        """Send error notification to user."""
        await self.hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "message": f"Failed to download usage data: {error_msg}. "
                           f"The integration will continue to work for account data, but usage statistics may be incomplete.",
                "title": "Contact Energy - Download Error",
                "notification_id": f"{DOMAIN}_download_error_{self._icp}"
            }
        )

    async def _load_stored_data(self):
        """Load previously stored statistics data."""
        try:
            store = Store(self.hass, 1, self._storage_key)
            self._stored_data = await store.async_load() or {}
            if self._stored_data:
                last_update = self._stored_data.get("last_update")
                if last_update:
                    last_update_date = datetime.fromisoformat(last_update)
                    days_since_update = (datetime.now() - last_update_date).days
                    if days_since_update < 2:
                        self._initial_download_complete = True
                        self._state = self._stored_data.get("total_usage", 0)
                        # Reduce log level to debug to avoid excessive info logs
                        _LOGGER.debug("Loaded cached usage data for %s: %.2f kWh", self._icp, self._state)
        except Exception as error:
            # Reduce log level to debug to avoid excessive warnings
            _LOGGER.debug("Failed to load stored data for %s: %s", self._icp, error)
            self._stored_data = {}

    async def _save_stored_data(self, total_usage: float, statistics_data: dict):
        """Save statistics data to storage."""
        try:
            store = Store(self.hass, 1, self._storage_key)
            data = {
                "last_update": datetime.now().isoformat(),
                "total_usage": total_usage,
                "statistics": statistics_data,
                "usage_days": self._usage_days
            }
            await store.async_save(data)
        except Exception as error:
            # Reduce log level to debug to avoid excessive warnings
            _LOGGER.debug("Failed to save stored data for %s: %s", self._icp, error)
            self._stored_data = data
            _LOGGER.debug("Saved usage data for %s: %.2f kWh", self._icp, total_usage)
            
        except Exception as error:
            _LOGGER.warning("Failed to save stored data for %s: %s", self._icp, error)

    @staticmethod
    def _safe_float(value: Any) -> float:
        """Safely convert value to float."""
        try:
            return float(value) if value is not None else 0.0
        except (TypeError, ValueError):
            return 0.0

    async def _add_statistics(
        self, 
        kwh_stats: list, 
        dollar_stats: list, 
        free_kwh_stats: list, 
        currency: str
    ) -> None:
        """Add statistics to Home Assistant."""
        
        # Main electricity consumption
        kwh_metadata = StatisticMetaData(
            has_mean=False,
            has_sum=True,
            name=f"Contact Energy - Electricity ({self._icp})",
            source=DOMAIN,
            statistic_id=f"{DOMAIN}:energy_consumption",
            unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        )
        async_add_external_statistics(self.hass, kwh_metadata, kwh_stats)

        # Electricity cost
        dollar_metadata = StatisticMetaData(
            has_mean=False,
            has_sum=True,
            name=f"Contact Energy - Electricity Cost ({self._icp})",
            source=DOMAIN,
            statistic_id=f"{DOMAIN}:energy_consumption_in_dollars",
            unit_of_measurement=currency,
        )
        async_add_external_statistics(self.hass, dollar_metadata, dollar_stats)

        # Free electricity
        free_kwh_metadata = StatisticMetaData(
            has_mean=False,
            has_sum=True,
            name=f"Contact Energy - Free Electricity ({self._icp})",
            source=DOMAIN,
            statistic_id=f"{DOMAIN}:free_energy_consumption",
            unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        )
        async_add_external_statistics(self.hass, free_kwh_metadata, free_kwh_stats)