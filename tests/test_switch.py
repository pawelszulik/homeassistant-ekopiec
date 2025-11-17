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


def test_switch_zima_lato_is_off(mock_coordinator):
    """Test zima_lato switch is_off (winter mode)."""
    switch = EkopiecSwitch(
        mock_coordinator,
        "zima_lato",
        {"name": "Tryb Zima/Lato", "icon": "mdi:snowflake-thermometer"}
    )
    
    # zima_lato = 0 means winter (off)
    assert switch.is_on is False


def test_switch_tryb_auto_is_on(mock_coordinator):
    """Test tryb_auto_state switch is_on (auto mode)."""
    switch = EkopiecSwitch(
        mock_coordinator,
        "tryb_auto_state",
        {"name": "Tryb Pracy", "icon": "mdi:auto-mode"}
    )
    
    # tryb_auto_state = 1 means auto (on)
    assert switch.is_on is True


@pytest.mark.asyncio
async def test_switch_turn_on(mock_coordinator):
    """Test turn on switch."""
    mock_coordinator.set_parameter_with_limit = AsyncMock(return_value=True)
    mock_coordinator.async_request_refresh = AsyncMock()
    
    switch = EkopiecSwitch(
        mock_coordinator,
        "zima_lato",
        {"name": "Tryb Zima/Lato", "icon": "mdi:snowflake-thermometer"}
    )
    
    await switch.async_turn_on()
    
    mock_coordinator.set_parameter_with_limit.assert_called_once_with("zima_lato", "1")
    mock_coordinator.async_request_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_switch_turn_off(mock_coordinator):
    """Test turn off switch."""
    mock_coordinator.set_parameter_with_limit = AsyncMock(return_value=True)
    mock_coordinator.async_request_refresh = AsyncMock()
    
    switch = EkopiecSwitch(
        mock_coordinator,
        "tryb_auto_state",
        {"name": "Tryb Pracy", "icon": "mdi:auto-mode"}
    )
    
    await switch.async_turn_off()
    
    mock_coordinator.set_parameter_with_limit.assert_called_once_with("tryb_auto_state", "0")
    mock_coordinator.async_request_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_switch_turn_on_failure(mock_coordinator):
    """Test turn on switch with failure."""
    mock_coordinator.set_parameter_with_limit = AsyncMock(return_value=False)
    mock_coordinator.async_request_refresh = AsyncMock()
    
    switch = EkopiecSwitch(
        mock_coordinator,
        "zima_lato",
        {"name": "Tryb Zima/Lato", "icon": "mdi:snowflake-thermometer"}
    )
    
    await switch.async_turn_on()
    
    # Should not refresh if set failed
    mock_coordinator.async_request_refresh.assert_not_called()
