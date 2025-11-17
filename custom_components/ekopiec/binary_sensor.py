"""Binary sensor platform for ekopiec integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .coordinator import EkopiecDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Output status sensors (read-only)
OUTPUT_TYPES: dict[str, dict[str, Any]] = {
    "out_pomp1": {
        "name": "Pompa 1",
        "device_class": BinarySensorDeviceClass.RUNNING,
    },
    "out_cwu": {
        "name": "Pompa CWU",
        "device_class": BinarySensorDeviceClass.RUNNING,
    },
    "out_miesz": {
        "name": "Pompa dodatkowa",
        "device_class": BinarySensorDeviceClass.RUNNING,
    },
    "out_dm": {
        "name": "Dmuchawa",
        "device_class": BinarySensorDeviceClass.RUNNING,
    },
    "out_zaw4d": {
        "name": "Zawór 4D",
        "device_class": BinarySensorDeviceClass.OPENING,
    },
}

# Alarm sensors
ALARM_TYPES: dict[str, dict[str, Any]] = {
    "alarm_kot_przegrzanie": {
        "name": "Boiler Overheating",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_kot_niska_temp": {
        "name": "Boiler Low Temperature",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_paliwo_brak": {
        "name": "No Fuel",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_paliwo_niski": {
        "name": "Low Fuel",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_cwu_przegrzanie": {
        "name": "DHW Overheating",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_cwu_niska_temp": {
        "name": "DHW Low Temperature",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_cisnienie": {
        "name": "Pressure Alarm",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_pompa_kotla": {
        "name": "Boiler Pump Failure",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_pompa_cwu": {
        "name": "DHW Pump Failure",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_dmuchawa": {
        "name": "Blower Failure",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_podajnik": {
        "name": "Feeder Failure",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_zapalarka": {
        "name": "Igniter Failure",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_czujnik_temp": {
        "name": "Temperature Sensor Failure",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_czujnik_cisnienia": {
        "name": "Pressure Sensor Failure",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_komunikacja": {
        "name": "Communication Error",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_zasilanie": {
        "name": "Power Supply Error",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_ob1": {
        "name": "Circuit 1 Alarm",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_ob2": {
        "name": "Circuit 2 Alarm",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_ob3": {
        "name": "Circuit 3 Alarm",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_ob4": {
        "name": "Circuit 4 Alarm",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_ob5": {
        "name": "Circuit 5 Alarm",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_ob6": {
        "name": "Circuit 6 Alarm",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_ogolny": {
        "name": "General Alarm",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
    "alarm_serwis": {
        "name": "Service Required",
        "device_class": BinarySensorDeviceClass.PROBLEM,
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor entities."""
    coordinator: EkopiecDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    
    # Always create output status sensors (they are essential for monitoring)
    for output_key, output_config in OUTPUT_TYPES.items():
        entities.append(EkopiecBinarySensor(coordinator, output_key, output_config))
    
    # Check if alarms should be shown
    if entry.options.get("show_alarms", False):
        for alarm_key, alarm_config in ALARM_TYPES.items():
            entities.append(EkopiecBinarySensor(coordinator, alarm_key, alarm_config))
    else:
        _LOGGER.debug("Alarm entities disabled in options")
    
    async_add_entities(entities)


class EkopiecBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of an ekopiec binary sensor."""
    
    def __init__(
        self,
        coordinator: EkopiecDataUpdateCoordinator,
        sensor_key: str,
        config: dict[str, Any],
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._config = config
        device_sn = coordinator.data.get("device_sn", "unknown")
        self._attr_unique_id = f"{device_sn}_{sensor_key}"
        self._attr_has_entity_name = True
        self._attr_name = config["name"]
        self._attr_device_class = config.get("device_class")
    
    @property
    def device_info(self):
        """Return device info."""
        return self.coordinator.device_info
    
    @property
    def is_on(self) -> bool:
        """Return if the binary sensor is on."""
        value = self.coordinator.data.get(self._sensor_key)
        if value is None:
            return False
        
        # Convert to boolean - handle various formats
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in ("1", "on", "true", "yes", "active", "alarm")
        return False
