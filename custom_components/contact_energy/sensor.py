"""Contact Energy sensors - consolidated implementation."""

import logging
from datetime import datetime, timedelta
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

    # Create all sensors
    sensors = [
        # Usage sensor (special handling for statistics)
        ContactEnergyUsageSensor(
            coordinator,
            api,
            icp,
            usage_days
        ),
        # Account sensors
        ContactEnergyAccountSensor(
            coordinator,
            icp,
            SENSOR_ACCOUNT_BALANCE_NAME,
            CURRENCY_DOLLAR,
            "mdi:cash",
            SensorStateClass.MEASUREMENT,
            SensorDeviceClass.MONETARY,
            lambda data: data.get("accountDetail", {}).get("accountBalance", {}).get("currentBalance"),
        ),
        ContactEnergyAccountSensor(
            coordinator,
            icp,
            SENSOR_NEXT_BILL_AMOUNT_NAME,
            CURRENCY_DOLLAR,
            "mdi:cash-clock",
            SensorStateClass.MEASUREMENT,
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
            SensorStateClass.MEASUREMENT,
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


def _parse_date(date_str: str) -> str | None:
    """Parse date string from Contact Energy API."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%d %b %Y").date().isoformat()
    except (ValueError, TypeError):
        return None


def _parse_meter_reading_date(data: dict, field_name: str) -> str | None:
    """Parse meter reading date from nested structure."""
    try:
        contracts = data.get("accountDetail", {}).get("contracts", [])
        if contracts and contracts[0].get("devices"):
            devices = contracts[0]["devices"]
            if devices and devices[0].get("registers"):
                registers = devices[0]["registers"]
                if registers:
                    date_str = registers[0].get(field_name)
                    return _parse_date(date_str)
    except (IndexError, KeyError, TypeError):
        pass
    return None


class ContactEnergyBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Contact Energy sensors."""

    def __init__(
        self,
        coordinator,
        icp: str,
        name: str,
        unit: str | None,
        icon: str,
        state_class: SensorStateClass | None = None,
        device_class: SensorDeviceClass | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._icp = icp
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{icp}_{name.lower().replace(' ', '_')}"
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_state_class = state_class
        self._attr_device_class = device_class

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._icp)},
            "name": f"{NAME} - {self._icp}",
            "manufacturer": NAME,
            "model": "Smart Meter",
        }


class ContactEnergyAccountSensor(ContactEnergyBaseSensor):
    """Sensor for Contact Energy account information."""

    def __init__(
        self,
        coordinator,
        icp: str,
        name: str,
        unit: str | None,
        icon: str,
        state_class: SensorStateClass | None,
        device_class: SensorDeviceClass | None,
        value_fn: Callable[[dict], Any],
    ) -> None:
        """Initialize the account sensor."""
        super().__init__(coordinator, icp, name, unit, icon, state_class, device_class)
        self._value_fn = value_fn

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
        if self.coordinator.last_update_success:
            attrs["last_updated"] = self.coordinator.last_update_success.isoformat()
        
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

    @property
    def native_value(self) -> float:
        """Return the current total usage."""
        return self._state

    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state."""
        return False

    async def async_update(self) -> None:
        """Update usage data and statistics."""
        # Only update usage data every 8 hours or if never updated
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
        """Fetch usage data and update Home Assistant statistics."""
        if not self._api._api_token and not await self._api.async_login():
            _LOGGER.error("Failed to login for usage data")
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

        for i in range(self._usage_days):
            current_date = today - timedelta(days=self._usage_days - i)
            _LOGGER.debug("Fetching usage data for %s", current_date.strftime("%Y-%m-%d"))
            
            response = await self._api.get_usage(
                str(current_date.year), 
                str(current_date.month), 
                str(current_date.day)
            )

            if not response:
                _LOGGER.debug("No data available for %s", current_date.strftime("%Y-%m-%d"))
                continue

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

        # Update Home Assistant statistics
        await self._add_statistics(kwh_statistics, dollar_statistics, free_kwh_statistics, currency)
        self._state = kwh_running_sum

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