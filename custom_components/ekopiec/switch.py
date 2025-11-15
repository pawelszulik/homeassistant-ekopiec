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
    "pompa_kotla": {
        "name": "Boiler Pump",
        "icon": "mdi:pump",
    },
    "pompa_cwu": {
        "name": "DHW Pump",
        "icon": "mdi:pump",
    },
    "pompa_ob1": {
        "name": "Circuit 1 Pump",
        "icon": "mdi:pump",
    },
    "pompa_ob2": {
        "name": "Circuit 2 Pump",
        "icon": "mdi:pump",
    },
    "pompa_ob3": {
        "name": "Circuit 3 Pump",
        "icon": "mdi:pump",
    },
    "pompa_ob4": {
        "name": "Circuit 4 Pump",
        "icon": "mdi:pump",
    },
    "dmuchawa": {
        "name": "Blower",
        "icon": "mdi:fan",
    },
    "zawor_mieszajacy": {
        "name": "Mixing Valve",
        "icon": "mdi:valve",
    },
    "zawor_trzydrogi": {
        "name": "Three-Way Valve",
        "icon": "mdi:valve",
    },
    "podajnik": {
        "name": "Feeder",
        "icon": "mdi:conveyor-belt",
    },
    "zapalarka": {
        "name": "Igniter",
        "icon": "mdi:fire",
    },
    "wentylator": {
        "name": "Fan",
        "icon": "mdi:fan",
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch entities."""
    coordinator: EkopiecDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Check if switches should be shown
    if not entry.options.get("show_switches", True):
        _LOGGER.debug("Switch entities disabled in options")
        return
    
    entities = []
    for switch_key, switch_config in SWITCH_TYPES.items():
        # Create entity even if data not available (will show as unavailable)
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

