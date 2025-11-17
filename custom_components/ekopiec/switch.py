"""Switch platform for ekopiec integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .coordinator import EkopiecDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SWITCH_TYPES: dict[str, dict[str, Any]] = {
    # Operating mode switches
    "zima_lato": {
        "name": "Tryb Zima/Lato",
        "icon": "mdi:snowflake-thermometer",
        "description": "Przełącz między trybem zimowym (0) a letnim (1)",
    },
    "tryb_auto_state": {
        "name": "Tryb Pracy",
        "icon": "mdi:auto-mode",
        "description": "Przełącz między trybem ręcznym (0) a automatycznym (1)",
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch entities."""
    coordinator: EkopiecDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for switch_key, switch_config in SWITCH_TYPES.items():
        entities.append(EkopiecSwitch(coordinator, switch_key, switch_config))
    
    async_add_entities(entities)


class EkopiecSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of an ekopiec switch."""
    
    def __init__(
        self,
        coordinator: EkopiecDataUpdateCoordinator,
        switch_key: str,
        config: dict[str, Any],
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._switch_key = switch_key
        self._config = config
        device_sn = coordinator.data.get("device_sn", "unknown")
        self._attr_unique_id = f"{device_sn}_{switch_key}"
        self._attr_has_entity_name = True
        self._attr_name = config["name"]
        if "icon" in config:
            self._attr_icon = config["icon"]
    
    @property
    def device_info(self):
        """Return device info."""
        return self.coordinator.device_info
    
    @property
    def is_on(self) -> bool:
        """Return if the switch is on."""
        value = self.coordinator.data.get(self._switch_key)
        if value is None:
            return False
        
        # Convert to boolean - handle various formats
        # For zima_lato: 0=zima (off), 1=lato (on)
        # For tryb_auto_state: 0=ręczny (off), 1=auto (on)
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in ("1", "on", "true", "yes")
        return False
    
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        success = await self.coordinator.set_parameter_with_limit(self._switch_key, "1")
        
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to turn on %s", self._switch_key)
    
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        success = await self.coordinator.set_parameter_with_limit(self._switch_key, "0")
        
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to turn off %s", self._switch_key)
