"""Climate platform for ekopiec integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, HEATING_CIRCUITS
from .coordinator import EkopiecDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# HVAC modes mapping
HVAC_MODE_MAP = {
    "0": HVACMode.OFF,
    "1": HVACMode.HEAT,
    "2": HVACMode.AUTO,
    "3": HVACMode.COOL,
}

HVAC_MODE_REVERSE = {v: k for k, v in HVAC_MODE_MAP.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up climate entities."""
    coordinator: EkopiecDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Check if climate entities should be shown
    if not entry.options.get("show_climate", True):
        _LOGGER.debug("Climate entities disabled in options")
        return
    
    entities = []
    for circuit_num in range(1, HEATING_CIRCUITS + 1):
        circuit_type = coordinator.data.get(f"ob{circuit_num}_typ")
        if circuit_type and circuit_type != "0":
            entities.append(EkopiecClimate(coordinator, circuit_num))
    
    async_add_entities(entities)


class EkopiecClimate(CoordinatorEntity, ClimateEntity):
    """Representation of an ekopiec climate entity."""
    
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    
    def __init__(
        self,
        coordinator: EkopiecDataUpdateCoordinator,
        circuit_num: int,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._circuit_num = circuit_num
        device_sn = coordinator.data.get("device_sn", "unknown")
        self._attr_unique_id = f"{device_sn}_climate_ob{circuit_num}"
        self._attr_has_entity_name = True
        self._attr_name = f"Heating Circuit {circuit_num}"
    
    @property
    def device_info(self):
        """Return device info."""
        return self.coordinator.device_info
    
    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        temp_key = f"ob{self._circuit_num}_temp"
        value = self.coordinator.data.get(temp_key)
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        temp_key = f"ob{self._circuit_num}_tzad"
        value = self.coordinator.data.get(temp_key)
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        mode_key = f"ob{self._circuit_num}_tryb"
        mode_value = self.coordinator.data.get(mode_key, "0")
        return HVAC_MODE_MAP.get(str(mode_value), HVACMode.OFF)
    
    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        
        temp_key = f"ob{self._circuit_num}_tzad"
        success = await self.coordinator.set_parameter_with_limit(temp_key, temperature)
        
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set temperature for circuit %d", self._circuit_num)
    
    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target HVAC mode."""
        mode_key = f"ob{self._circuit_num}_tryb"
        mode_value = HVAC_MODE_REVERSE.get(hvac_mode, "0")
        
        success = await self.coordinator.set_parameter_with_limit(mode_key, mode_value)
        
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set HVAC mode for circuit %d", self._circuit_num)
    
    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        await self.async_set_hvac_mode(HVACMode.HEAT)
    
    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        await self.async_set_hvac_mode(HVACMode.OFF)

