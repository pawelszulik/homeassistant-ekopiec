"""Sensor platform for ekopiec integration."""
from __future__ import annotations

from datetime import datetime
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
    
    entities = []
    
    for sensor_key, sensor_config in SENSOR_TYPES.items():
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
        device_sn = (coordinator.data or {}).get("device_sn", "unknown")
        self._attr_unique_id = f"{device_sn}_{sensor_key}"
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
    def available(self) -> bool:
        """Return if entity is available."""
        if not self.coordinator.last_update_success:
            return False
        if not self.coordinator.data:
            return False
        return self._sensor_key in self.coordinator.data
    
    @property
    def native_value(self) -> str | float | datetime | None:
        """Return the state of the sensor."""
        value = self.coordinator.data.get(self._sensor_key)
        if value is None:
            return None
        
        # Handle timestamp sensors - convert ISO string to datetime object
        if self._config.get("device_class") == SensorDeviceClass.TIMESTAMP:
            if isinstance(value, str):
                try:
                    # Parse ISO format string to datetime
                    dt = datetime.fromisoformat(value)
                    # If datetime is naive, make it aware using HA timezone
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=self.coordinator.hass.config.time_zone)
                    return dt
                except (ValueError, TypeError) as err:
                    _LOGGER.warning("Cannot parse timestamp for %s: %s", self._sensor_key, err)
                    return None
        
        # Try to convert to float for numeric values
        try:
            return float(value)
        except (ValueError, TypeError):
            return str(value)
