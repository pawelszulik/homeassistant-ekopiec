"""Sensor platform for ekopiec integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfEnergy,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .coordinator import EkopiecDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Temperature sensors
SENSOR_TYPES: dict[str, dict[str, Any]] = {
    # Boiler temperatures
    "kot_value": {
        "name": "Boiler Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kot_tzad": {
        "name": "Boiler Target Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "tpow_value": {
        "name": "Return Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "tcwu_value": {
        "name": "DHW Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "tcwu_tzad": {
        "name": "DHW Target Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Circuit temperatures
    "ob1_temp": {
        "name": "Circuit 1 Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "ob2_temp": {
        "name": "Circuit 2 Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "ob3_temp": {
        "name": "Circuit 3 Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "ob4_temp": {
        "name": "Circuit 4 Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "ob5_temp": {
        "name": "Circuit 5 Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "ob6_temp": {
        "name": "Circuit 6 Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Fuel sensors
    "paliwo_poziom": {
        "name": "Fuel Level",
        "device_class": None,
        "unit": PERCENTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "paliwo_czas_pracy": {
        "name": "Fuel Runtime",
        "device_class": SensorDeviceClass.DURATION,
        "unit": UnitOfTime.HOURS,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "paliwo_data_zasypania": {
        "name": "Fuel Refill Date",
        "device_class": SensorDeviceClass.TIMESTAMP,
        "unit": None,
        "state_class": None,
    },
    "paliwo_ilosc": {
        "name": "Fuel Amount",
        "device_class": None,
        "unit": "kg",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "paliwo_zuzycie": {
        "name": "Fuel Consumption",
        "device_class": None,
        "unit": "kg/h",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "paliwo_pozostalo": {
        "name": "Fuel Remaining",
        "device_class": None,
        "unit": "kg",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "paliwo_dni_do_zasypania": {
        "name": "Days Until Refill",
        "device_class": None,
        "unit": "days",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # DHW/CWU sensors
    "cwu_cisnienie": {
        "name": "DHW Pressure",
        "device_class": None,
        "unit": "bar",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "cwu_poziom": {
        "name": "DHW Level",
        "device_class": None,
        "unit": PERCENTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "cwu_czas_pracy": {
        "name": "DHW Runtime",
        "device_class": SensorDeviceClass.DURATION,
        "unit": UnitOfTime.HOURS,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "cwu_tryb": {
        "name": "DHW Mode",
        "device_class": None,
        "unit": None,
        "state_class": None,
    },
    "cwu_status": {
        "name": "DHW Status",
        "device_class": None,
        "unit": None,
        "state_class": None,
    },
    "cwu_temperatura_min": {
        "name": "DHW Min Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "cwu_temperatura_max": {
        "name": "DHW Max Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Other sensors
    "device_soft_version": {
        "name": "Software Version",
        "device_class": None,
        "unit": None,
        "state_class": None,
    },
    "device_hard_version": {
        "name": "Hardware Version",
        "device_class": None,
        "unit": None,
        "state_class": None,
    },
    "device_type": {
        "name": "Device Type",
        "device_class": None,
        "unit": None,
        "state_class": None,
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    coordinator: EkopiecDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Check filter options
    show_temps = entry.options.get("show_temperatures", True)
    show_fuel = entry.options.get("show_fuel", True)
    show_dhw = entry.options.get("show_dhw", True)
    
    entities = []
    
    for sensor_key, sensor_config in SENSOR_TYPES.items():
        # Skip based on options
        if "temp" in sensor_key.lower() or "kot" in sensor_key.lower() or "tpow" in sensor_key.lower() or "tcwu" in sensor_key.lower():
            if not show_temps:
                _LOGGER.debug("Skipping temperature sensor: %s", sensor_key)
                continue
        
        if "paliwo" in sensor_key.lower() or "fuel" in sensor_config["name"].lower():
            if not show_fuel:
                _LOGGER.debug("Skipping fuel sensor: %s", sensor_key)
                continue
        
        if "cwu" in sensor_key.lower() or "dhw" in sensor_key.lower():
            if not show_dhw:
                _LOGGER.debug("Skipping DHW sensor: %s", sensor_key)
                continue
        
        if sensor_key in coordinator.data:
            entities.append(EkopiecSensor(coordinator, sensor_key, sensor_config))
    
    async_add_entities(entities)


class EkopiecSensor(CoordinatorEntity, SensorEntity):
    """Representation of an ekopiec sensor."""
    
    def __init__(
        self,
        coordinator: EkopiecDataUpdateCoordinator,
        sensor_key: str,
        config: dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._config = config
        self._attr_unique_id = f"{coordinator.data.get('device_sn', 'unknown')}_{sensor_key}"
        self._attr_has_entity_name = True
        self._attr_name = config["name"]
        
        # Set device class and unit
        if config.get("device_class"):
            self._attr_device_class = config["device_class"]
        if config.get("unit"):
            self._attr_native_unit_of_measurement = config["unit"]
        if config.get("state_class"):
            self._attr_state_class = config["state_class"]
    
    @property
    def device_info(self):
        """Return device info."""
        return self.coordinator.device_info
    
    @property
    def native_value(self) -> str | float | None:
        """Return the state of the sensor."""
        value = self.coordinator.data.get(self._sensor_key)
        if value is None:
            return None
        
        # Try to convert to float for numeric values
        try:
            return float(value)
        except (ValueError, TypeError):
            return str(value)

