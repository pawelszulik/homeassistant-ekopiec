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
    "tkot_value": {
        "name": "Temperatura kotła",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "tpow_value": {
        "name": "Temperatura powrotu",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "tpod_value": {
        "name": "Temperatura podajnika",
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
    "t1_value": {
        "name": "Temperatura za zaworem",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "tsp_value": {
        "name": "Temperatura spalin",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Blower/Fan sensors
    "dm_rms": {
        "name": "Wartość skuteczna dmuchawy/nawiewnika",
        "device_class": None,
        "unit": PERCENTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "act_dm_speed": {
        "name": "Aktualna moc dmuchawy",
        "device_class": None,
        "unit": PERCENTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Regulator parameters (read-only sensors)
    "rr_g_pod_off": {
        "name": "Czas postoju podajnika",
        "device_class": SensorDeviceClass.DURATION,
        "unit": UnitOfTime.SECONDS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "rr_g_pod_on": {
        "name": "Czas pracy podajnika",
        "device_class": SensorDeviceClass.DURATION,
        "unit": UnitOfTime.SECONDS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "rr_rsp_dm_speed": {
        "name": "Minimalna moc dmuchawy",
        "device_class": None,
        "unit": PERCENTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "rr_rsp_tmax": {
        "name": "Maksymalna temperatura spalin",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "rr_rsp_en": {
        "name": "Regulator temperatury spalin",
        "device_class": None,
        "unit": None,
        "state_class": None,
    },
    "rr_g_dm_speed": {
        "name": "Moc dmuchawy",
        "device_class": None,
        "unit": PERCENTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Setpoint sensors (read-only)
    "kot_tzad": {
        "name": "Temperatura zadana kotła",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "cwu_tzad": {
        "name": "Temperatura zadana CWU",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "pomp_ton": {
        "name": "Temperatura załączenia pomp",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Feeder parameters (read-only)
    "p_pod_on": {
        "name": "Czas pracy podajnika - Podtrzymanie",
        "device_class": SensorDeviceClass.DURATION,
        "unit": UnitOfTime.SECONDS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "p_pod_off": {
        "name": "Czas postoju podajnika - Podtrzymanie",
        "device_class": SensorDeviceClass.DURATION,
        "unit": UnitOfTime.SECONDS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "p_pod_wait": {
        "name": "Czas krótkiej przerwy - Podtrzymanie",
        "device_class": SensorDeviceClass.DURATION,
        "unit": UnitOfTime.SECONDS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "p_pod_cnt": {
        "name": "Ilość powtórzeń - Podtrzymanie",
        "device_class": None,
        "unit": "repetitions",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Operating modes (read-only sensors)
    "zima_lato": {
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
    # Fuel sensors
    "fuel_level": {
        "name": "Poziom paliwa w zasobniku",
        "device_class": None,
        "unit": PERCENTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "pod_run_time_str": {
        "name": "Czas pracy podajnika",
        "device_class": None,
        "unit": None,
        "state_class": None,
    },
    # Valve position
    "ob1_zaw4d_pos": {
        "name": "Pozycja zaworu 4D",
        "device_class": None,
        "unit": PERCENTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Date/Time sensors
    "datetime": {
        "name": "Aktualna data",
        "device_class": SensorDeviceClass.TIMESTAMP,
        "unit": None,
        "state_class": None,
    },
    "add_fuel_time": {
        "name": "Ostatnia data zasypu",
        "device_class": SensorDeviceClass.TIMESTAMP,
        "unit": None,
        "state_class": None,
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
        if "temp" in sensor_key.lower() or "tkot" in sensor_key.lower() or "tpow" in sensor_key.lower() or "tcwu" in sensor_key.lower():
            if not show_temps:
                _LOGGER.debug("Skipping temperature sensor: %s", sensor_key)
                continue
        
        # Check for fuel sensors
        is_fuel_sensor = (
            "fuel" in sensor_key.lower() or
            "pod_run" in sensor_key.lower()
        )
        
        if is_fuel_sensor:
            if not show_fuel:
                _LOGGER.debug("Skipping fuel sensor: %s (show_fuel=%s)", sensor_key, show_fuel)
                continue
            _LOGGER.debug("Creating fuel sensor: %s", sensor_key)
        
        if "cwu" in sensor_key.lower():
            if not show_dhw:
                _LOGGER.debug("Skipping DHW sensor: %s", sensor_key)
                continue
        
        # Create entity even if data not available (will show as unavailable)
        entities.append(EkopiecSensor(coordinator, sensor_key, sensor_config))
    
    _LOGGER.info("Created %d sensor entities", len(entities))
    
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
