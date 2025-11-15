"""Tests for climate entities."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from custom_components.ekopiec.climate import EkopiecClimate, async_setup_entry, HVAC_MODE_MAP
from homeassistant.components.climate import HVACMode
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry


@pytest.mark.asyncio
async def test_climate_setup(hass: HomeAssistant, mock_config_entry, mock_coordinator):
    """Test climate setup."""
    hass.data["ekopiec"] = {"test_entry_id": mock_coordinator}
    
    async_add_entities = AsyncMock()
    
    await async_setup_entry(hass, mock_config_entry, async_add_entities)
    
    assert async_add_entities.called


def test_climate_current_temperature(mock_coordinator):
    """Test current temperature property."""
    climate = EkopiecClimate(mock_coordinator, 1)
    
    assert climate.current_temperature == 45.0


def test_climate_target_temperature(mock_coordinator):
    """Test target temperature property."""
    climate = EkopiecClimate(mock_coordinator, 1)
    
    assert climate.target_temperature == 50.0


def test_climate_hvac_mode(mock_coordinator):
    """Test HVAC mode property."""
    climate = EkopiecClimate(mock_coordinator, 1)
    
    assert climate.hvac_mode == HVACMode.HEAT


@pytest.mark.asyncio
async def test_climate_set_temperature(mock_coordinator):
    """Test set temperature."""
    mock_coordinator.set_parameter_with_limit = AsyncMock(return_value=True)
    mock_coordinator.async_request_refresh = AsyncMock()
    
    climate = EkopiecClimate(mock_coordinator, 1)
    await climate.async_set_temperature(temperature=55.0)
    
    mock_coordinator.set_parameter_with_limit.assert_called_once_with("ob1_tzad", 55.0)
    mock_coordinator.async_request_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_climate_set_hvac_mode(mock_coordinator):
    """Test set HVAC mode."""
    mock_coordinator.set_parameter_with_limit = AsyncMock(return_value=True)
    mock_coordinator.async_request_refresh = AsyncMock()
    
    climate = EkopiecClimate(mock_coordinator, 1)
    await climate.async_set_hvac_mode(HVACMode.AUTO)
    
    mock_coordinator.set_parameter_with_limit.assert_called_once_with("ob1_tryb", "2")
    mock_coordinator.async_request_refresh.assert_called_once()

