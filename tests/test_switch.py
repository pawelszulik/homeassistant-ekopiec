"""Tests for switch entities."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from custom_components.ekopiec.switch import EkopiecSwitch, async_setup_entry
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry


@pytest.mark.asyncio
async def test_switch_setup(hass: HomeAssistant, mock_config_entry, mock_coordinator):
    """Test switch setup."""
    hass.data["ekopiec"] = {"test_entry_id": mock_coordinator}
    
    async_add_entities = AsyncMock()
    
    await async_setup_entry(hass, mock_config_entry, async_add_entities)
    
    assert async_add_entities.called


def test_switch_is_on(mock_coordinator):
    """Test switch is_on property."""
    switch = EkopiecSwitch(
        mock_coordinator,
        "pompa_kotla",
        {"name": "Boiler Pump", "icon": "mdi:pump"}
    )
    
    assert switch.is_on is True


def test_switch_is_off(mock_coordinator):
    """Test switch is_off property."""
    switch = EkopiecSwitch(
        mock_coordinator,
        "pompa_cwu",
        {"name": "DHW Pump", "icon": "mdi:pump"}
    )
    
    assert switch.is_on is False


@pytest.mark.asyncio
async def test_switch_turn_on(mock_coordinator):
    """Test turn on switch."""
    mock_coordinator.set_parameter_with_limit = AsyncMock(return_value=True)
    mock_coordinator.async_request_refresh = AsyncMock()
    
    switch = EkopiecSwitch(
        mock_coordinator,
        "pompa_cwu",
        {"name": "DHW Pump", "icon": "mdi:pump"}
    )
    
    await switch.async_turn_on()
    
    mock_coordinator.set_parameter_with_limit.assert_called_once_with("pompa_cwu", "1")
    mock_coordinator.async_request_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_switch_turn_off(mock_coordinator):
    """Test turn off switch."""
    mock_coordinator.set_parameter_with_limit = AsyncMock(return_value=True)
    mock_coordinator.async_request_refresh = AsyncMock()
    
    switch = EkopiecSwitch(
        mock_coordinator,
        "pompa_kotla",
        {"name": "Boiler Pump", "icon": "mdi:pump"}
    )
    
    await switch.async_turn_off()
    
    mock_coordinator.set_parameter_with_limit.assert_called_once_with("pompa_kotla", "0")
    mock_coordinator.async_request_refresh.assert_called_once()

