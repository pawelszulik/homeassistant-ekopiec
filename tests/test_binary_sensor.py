"""Tests for binary sensor entities."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from custom_components.ekopiec.binary_sensor import EkopiecBinarySensor, async_setup_entry
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry


@pytest.mark.asyncio
async def test_binary_sensor_setup(hass: HomeAssistant, mock_config_entry, mock_coordinator):
    """Test binary sensor setup."""
    hass.data["ekopiec"] = {"test_entry_id": mock_coordinator}
    
    async_add_entities = AsyncMock()
    
    await async_setup_entry(hass, mock_config_entry, async_add_entities)
    
    # Should add both output sensors and alarm sensors
    assert async_add_entities.called


def test_output_sensor_is_on(mock_coordinator):
    """Test output binary sensor is_on when output active."""
    mock_coordinator.data["out_pomp1"] = "1"
    
    sensor = EkopiecBinarySensor(
        mock_coordinator,
        "out_pomp1",
        {
            "name": "Pompa 1",
            "device_class": "running",
        }
    )
    
    assert sensor.is_on is True


def test_output_sensor_is_off(mock_coordinator):
    """Test output binary sensor is_off when output inactive."""
    mock_coordinator.data["out_cwu"] = "0"
    
    sensor = EkopiecBinarySensor(
        mock_coordinator,
        "out_cwu",
        {
            "name": "Pompa CWU",
            "device_class": "running",
        }
    )
    
    assert sensor.is_on is False


def test_alarm_sensor_is_on(mock_coordinator):
    """Test alarm binary sensor is_on when alarm active."""
    mock_coordinator.data["alarm_kot_przegrzanie"] = "1"
    
    alarm = EkopiecBinarySensor(
        mock_coordinator,
        "alarm_kot_przegrzanie",
        {
            "name": "Boiler Overheating",
            "device_class": "problem",
        }
    )
    
    assert alarm.is_on is True


def test_alarm_sensor_is_off(mock_coordinator):
    """Test alarm binary sensor is_off when alarm inactive."""
    alarm = EkopiecBinarySensor(
        mock_coordinator,
        "alarm_kot_przegrzanie",
        {
            "name": "Boiler Overheating",
            "device_class": "problem",
        }
    )
    
    assert alarm.is_on is False


def test_binary_sensor_string_values(mock_coordinator):
    """Test binary sensor with string values."""
    mock_coordinator.data["alarm_test"] = "active"
    
    alarm = EkopiecBinarySensor(
        mock_coordinator,
        "alarm_test",
        {
            "name": "Test Alarm",
            "device_class": "problem",
        }
    )
    
    assert alarm.is_on is True
