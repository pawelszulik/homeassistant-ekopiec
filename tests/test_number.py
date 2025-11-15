"""Tests for number entities."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from homeassistant.exceptions import HomeAssistantError

from custom_components.ekopiec.number import EkopiecNumber, async_setup_entry
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry


@pytest.mark.asyncio
async def test_number_setup(hass: HomeAssistant, mock_config_entry, mock_coordinator):
    """Test number setup."""
    hass.data["ekopiec"] = {"test_entry_id": mock_coordinator}
    
    async_add_entities = AsyncMock()
    
    await async_setup_entry(hass, mock_config_entry, async_add_entities)
    
    assert async_add_entities.called


def test_number_value(mock_coordinator):
    """Test number value property."""
    number = EkopiecNumber(
        mock_coordinator,
        "kot_tzad",
        {
            "name": "Boiler Target Temperature",
            "device_class": "temperature",
            "unit": "°C",
            "min_value": 10,
            "max_value": 85,
            "step": 0.5,
        }
    )
    
    assert number.native_value == 70.0


def test_number_min_max(mock_coordinator):
    """Test number min/max constraints."""
    number = EkopiecNumber(
        mock_coordinator,
        "kot_tzad",
        {
            "name": "Boiler Target Temperature",
            "device_class": "temperature",
            "unit": "°C",
            "min_value": 10,
            "max_value": 85,
            "step": 0.5,
        }
    )
    
    assert number.native_min_value == 10
    assert number.native_max_value == 85
    assert number.native_step == 0.5


@pytest.mark.asyncio
async def test_number_set_value_success(mock_coordinator):
    """Test successful set value."""
    mock_coordinator.set_parameter_with_limit = AsyncMock(return_value=True)
    mock_coordinator.async_request_refresh = AsyncMock()
    
    number = EkopiecNumber(
        mock_coordinator,
        "kot_tzad",
        {
            "name": "Boiler Target Temperature",
            "device_class": "temperature",
            "unit": "°C",
            "min_value": 10,
            "max_value": 85,
            "step": 0.5,
        }
    )
    
    await number.async_set_native_value(75.0)
    
    mock_coordinator.set_parameter_with_limit.assert_called_once_with("kot_tzad", 75.0)
    mock_coordinator.async_request_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_number_set_value_out_of_range(mock_coordinator):
    """Test set value out of range."""
    number = EkopiecNumber(
        mock_coordinator,
        "kot_tzad",
        {
            "name": "Boiler Target Temperature",
            "device_class": "temperature",
            "unit": "°C",
            "min_value": 10,
            "max_value": 85,
            "step": 0.5,
        }
    )
    
    with pytest.raises(ValueError):
        await number.async_set_native_value(100.0)


@pytest.mark.asyncio
async def test_number_set_value_failed(mock_coordinator):
    """Test set value when API call fails."""
    mock_coordinator.set_parameter_with_limit = AsyncMock(return_value=False)
    
    number = EkopiecNumber(
        mock_coordinator,
        "kot_tzad",
        {
            "name": "Boiler Target Temperature",
            "device_class": "temperature",
            "unit": "°C",
            "min_value": 10,
            "max_value": 85,
            "step": 0.5,
        }
    )
    
    with pytest.raises(HomeAssistantError):
        await number.async_set_native_value(75.0)

