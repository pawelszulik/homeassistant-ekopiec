"""Number platform for ekopiec integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .coordinator import EkopiecDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Define parameter ranges and validation
NUMBER_TYPES: dict[str, dict[str, Any]] = {
    # Boiler setpoints
    "kot_tzad": {
        "name": "Temperatura zadana kotła",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "min_value": 10,
        "max_value": 85,
        "step": 0.5,
    },
    "cwu_tzad": {
        "name": "Temperatura zadana CWU",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "min_value": 10,
        "max_value": 85,
        "step": 0.5,
    },
    "pomp_ton": {
        "name": "Temperatura załączenia pomp",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "min_value": 10,
        "max_value": 85,
        "step": 0.5,
    },
    # Feeder parameters - Maintenance mode
    "p_pod_on": {
        "name": "Czas pracy podajnika - Podtrzymanie",
        "device_class": SensorDeviceClass.DURATION,
        "unit": UnitOfTime.SECONDS,
        "min_value": 1,
        "max_value": 300,
        "step": 1,
    },
    "p_pod_off": {
        "name": "Czas postoju podajnika - Podtrzymanie",
        "device_class": SensorDeviceClass.DURATION,
        "unit": UnitOfTime.SECONDS,
        "min_value": 1,
        "max_value": 3600,
        "step": 1,
    },
    "p_pod_wait": {
        "name": "Czas krótkiej przerwy - Podtrzymanie",
        "device_class": SensorDeviceClass.DURATION,
        "unit": UnitOfTime.SECONDS,
        "min_value": 1,
        "max_value": 300,
        "step": 1,
    },
    "p_pod_cnt": {
        "name": "Ilość powtórzeń - Podtrzymanie",
        "unit": "repetitions",
        "min_value": 1,
        "max_value": 20,
        "step": 1,
    },
    # Regulator parameters - Feeder
    "rr_g_pod_off": {
        "name": "Czas postoju podajnika",
        "device_class": SensorDeviceClass.DURATION,
        "unit": UnitOfTime.SECONDS,
        "min_value": 0,
        "max_value": 300,
        "step": 1,
    },
    "rr_g_pod_on": {
        "name": "Czas pracy podajnika",
        "device_class": SensorDeviceClass.DURATION,
        "unit": UnitOfTime.SECONDS,
        "min_value": 0,
        "max_value": 300,
        "step": 1,
    },
    # Regulator parameters - Blower
    "rr_rsp_dm_speed": {
        "name": "Minimalna moc dmuchawy",
        "unit": PERCENTAGE,
        "min_value": 0,
        "max_value": 300,
        "step": 1,
    },
    "rr_rsp_tmax": {
        "name": "Maksymalna temperatura spalin",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "min_value": 0,
        "max_value": 300,
        "step": 1,
    },
    "rr_rsp_en": {
        "name": "Regulator temperatury spalin",
        "unit": None,
        "min_value": 0,
        "max_value": 1,
        "step": 1,
    },
    "rr_g_dm_speed": {
        "name": "Moc dmuchawy",
        "unit": PERCENTAGE,
        "min_value": 0,
        "max_value": 300,
        "step": 1,
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities."""
    coordinator: EkopiecDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Check if numbers should be shown
    if not entry.options.get("show_numbers", True):
        _LOGGER.debug("Number entities disabled in options")
        return
    
    entities = []
    for number_key, number_config in NUMBER_TYPES.items():
        # Create entity even if data not available (will show as unavailable)
        entities.append(EkopiecNumber(coordinator, number_key, number_config))
    
    async_add_entities(entities)


class EkopiecNumber(CoordinatorEntity, NumberEntity):
    """Representation of ekopiec number entity."""
    
    def __init__(
        self,
        coordinator: EkopiecDataUpdateCoordinator,
        number_key: str,
        config: dict[str, Any],
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._number_key = number_key
        self._config = config
        device_sn = coordinator.data.get("device_sn", "unknown")
        self._attr_unique_id = f"{device_sn}_{number_key}"
        self._attr_has_entity_name = True
        self._attr_name = config["name"]
        
        # Set value constraints
        self._attr_native_min_value = config.get("min_value", 0)
        self._attr_native_max_value = config.get("max_value", 100)
        self._attr_native_step = config.get("step", 1)
        
        # Set units and device class
        if "unit" in config:
            self._attr_native_unit_of_measurement = config["unit"]
        if "device_class" in config:
            self._attr_device_class = config["device_class"]
    
    @property
    def device_info(self):
        """Return device info."""
        return self.coordinator.device_info
    
    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        try:
            value = self.coordinator.data.get(self._number_key)
            if value is None:
                return None
            return float(value)
        except (ValueError, TypeError):
            return None
    
    async def async_set_native_value(self, value: float) -> None:
        """Set new value with validation.
        
        Args:
            value: New value to set
            
        Raises:
            ValueError: If value is out of range
        """
        # Validate value is within range
        if value < self._attr_native_min_value or value > self._attr_native_max_value:
            _LOGGER.error(
                "Value %s out of range [%s, %s] for %s",
                value,
                self._attr_native_min_value,
                self._attr_native_max_value,
                self._number_key
            )
            raise ValueError(
                f"Value must be between {self._attr_native_min_value} "
                f"and {self._attr_native_max_value}"
            )
        
        # Send to controller
        success = await self.coordinator.set_parameter_with_limit(
            self._number_key,
            value
        )
        
        if success:
            # Request refresh to get updated value
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set %s to %s", self._number_key, value)
            raise HomeAssistantError(
                f"Failed to set {self._attr_name} to {value}"
            )
