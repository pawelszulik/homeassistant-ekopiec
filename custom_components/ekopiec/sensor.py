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
        "name": "Temperatura Kot�a",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "kot_tzad": {
        "name": "Temperatura Zadana Kot�a",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "tpow_value": {
        "name": "Temperatura powrotu kot�a",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "tcwu_value": {
        "name": "Temperatura CWU",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "tcwu_tzad": {
        "name": "Temperatura zadana",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Exhaust/Flue temperature
    "tsp_value": {
        "name": "Temperatura spalin",
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
    # Fuel sensors
    "paliwo_poziom": {
        "name": "Poziom paliwa",
        "device_class": None,
        "unit": PERCENTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "paliwo_czas_pracy": {
        "name": "Czas pracy na paliwie",
        "device_class": SensorDeviceClass.DURATION,
        "unit": UnitOfTime.HOURS,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "paliwo_data_zasypania": {
        "name": "Data zasypania kot�a",
        "device_class": SensorDeviceClass.TIMESTAMP,
        "unit": None,
        "state_class": None,
    },
    "paliwo_ilosc": {
        "name": "Ilo�� w�gla",
        "device_class": None,
        "unit": "kg",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "paliwo_zuzycie": {
        "name": "Zu�ycie w kg\h",
        "device_class": None,
        "unit": "kg/h",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "paliwo_pozostalo": {
        "name": "Zosta�o w�gla",
        "device_class": None,
        "unit": "kg",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "paliwo_dni_do_zasypania": {
        "name": "Ilo�� do do zasypania",
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
    "act_dm_speed": {
        "name": "Aktualna moc dmuchawy",
        "device_class": None,
        "unit": PERCENTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Operating modes
    "zima_lato": {
        "name": "Tryb Zima/Lato",
        "device_class": None,
        "unit": None,
        "state_class": None,
    },
    "zima_lato_state": {
        "name": "Tryb Zima/Lato",
        "device_class": None,
        "unit": None,
        "state_class": None,
    },
    "tryb_auto_state": {
        "name": "Tryb Pracy",
        "device_class": None,
        "unit": None,
        "state_class": None,
    },
    # Valve 4D position sensors (for each circuit)
    "ob1_zaw4d_pos": {
        "name": "Zawór 4D Obwód 1 - Pozycja otwarcia",
        "device_class": None,
        "unit": PERCENTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Additional temperature sensors
    "tpod_value": {
        "name": "Temperatura podajnika",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "twew_value": {
        "name": "Temperatura wewnętrzna",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "tzew_value": {
        "name": "Temperatura zewnętrzna",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "t1_value": {
        "name": "Temperatura za zaworem",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "t2_value": {
        "name": "Temperatura wewnętrzna CO2",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Additional fuel sensors
    "fuel_level": {
        "name": "Poziom paliwa",
        "device_class": None,
        "unit": PERCENTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "fuel_level_enum": {
        "name": "Poziom paliwa (enum)",
        "device_class": None,
        "unit": None,
        "state_class": None,
    },
    "pod_run_time": {
        "name": "Czas pracy podajnika",
        "device_class": SensorDeviceClass.DURATION,
        "unit": UnitOfTime.HOURS,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "pod_run_time_str": {
        "name": "Czas pracy podajnika (tekst)",
        "device_class": None,
        "unit": None,
        "state_class": None,
    },
    "time_to_empty": {
        "name": "Czas do opróżnienia zasobnika",
        "device_class": SensorDeviceClass.DURATION,
        "unit": UnitOfTime.HOURS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "next_fuel_time": {
        "name": "Data kolejnego zasypu",
        "device_class": SensorDeviceClass.TIMESTAMP,
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
    
    _LOGGER.info(
        "Setting up sensors: show_temps=%s, show_fuel=%s, show_dhw=%s",
        show_temps, show_fuel, show_dhw
    )
    
    entities = []
    
    for sensor_key, sensor_config in SENSOR_TYPES.items():
        # Skip based on options
        if "temp" in sensor_key.lower() or "kot" in sensor_key.lower() or "tpow" in sensor_key.lower() or "tcwu" in sensor_key.lower():
            if not show_temps:
                _LOGGER.debug("Skipping temperature sensor: %s", sensor_key)
                continue
        
        # Check for fuel sensors - check both key and name (name might be in Polish now)
        is_fuel_sensor = (
            "paliwo" in sensor_key.lower() or 
            "fuel" in sensor_key.lower() or
            "fuel" in sensor_config.get("name", "").lower() or
            "paliwo" in sensor_config.get("name", "").lower() or
            "węgla" in sensor_config.get("name", "").lower() or
            "zasypania" in sensor_config.get("name", "").lower()
        )
        
        if is_fuel_sensor:
            if not show_fuel:
                _LOGGER.debug("Skipping fuel sensor: %s (show_fuel=%s)", sensor_key, show_fuel)
                continue
            _LOGGER.debug("Creating fuel sensor: %s", sensor_key)
        
        if "cwu" in sensor_key.lower() or "dhw" in sensor_key.lower():
            if not show_dhw:
                _LOGGER.debug("Skipping DHW sensor: %s", sensor_key)
                continue
        
        # Create entity even if data not available (will show as unavailable)
        entities.append(EkopiecSensor(coordinator, sensor_key, sensor_config))
    
    _LOGGER.info("Created %d sensor entities", len(entities))
    fuel_sensors = [e._sensor_key for e in entities if "paliwo" in e._sensor_key.lower()]
    if fuel_sensors:
        _LOGGER.info("Fuel sensors created: %s", fuel_sensors)
    else:
        _LOGGER.warning("No fuel sensors created! Check show_fuel option and sensor definitions.")
    
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

