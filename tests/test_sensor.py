"""Tests for sensor entities."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from custom_components.ekopiec.sensor import EkopiecSensor, async_setup_entry
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry


@pytest.mark.asyncio
async def test_sensor_setup(hass: HomeAssistant, mock_config_entry, mock_coordinator):
    """Test sensor setup."""
    hass.data["ekopiec"] = {"test_entry_id": mock_coordinator}
    
    async_add_entities = AsyncMock()
    
    await async_setup_entry(hass, mock_config_entry, async_add_entities)
    
    assert async_add_entities.called


def test_sensor_value(mock_coordinator):
    """Test sensor value property."""
    sensor = EkopiecSensor(
        mock_coordinator,
        "kot_value",
        {
            "name": "Boiler Temperature",
            "device_class": "temperature",
            "unit": "°C",
            "state_class": "measurement",
        }
    )
    
    value = sensor.native_value
    assert value == 65.5


def test_sensor_value_string(mock_coordinator):
    """Test sensor with string value."""
    mock_coordinator.data["device_type"] = "eCoal"
    sensor = EkopiecSensor(
        mock_coordinator,
        "device_type",
        {
            "name": "Device Type",
            "device_class": None,
            "unit": None,
            "state_class": None,
        }
    )
    
    value = sensor.native_value
    assert value == "eCoal"


def test_sensor_value_none(mock_coordinator):
    """Test sensor with None value."""
    sensor = EkopiecSensor(
        mock_coordinator,
        "nonexistent_key",
        {
            "name": "Nonexistent",
            "device_class": None,
            "unit": None,
            "state_class": None,
        }
    )
    
    value = sensor.native_value
    assert value is None

