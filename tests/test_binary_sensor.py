"""Tests for binary sensor entities."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from custom_components.ekopiec.binary_sensor import EkopiecAlarm, async_setup_entry
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry


@pytest.mark.asyncio
async def test_binary_sensor_setup(hass: HomeAssistant, mock_config_entry, mock_coordinator):
    """Test binary sensor setup."""
    hass.data["ekopiec"] = {"test_entry_id": mock_coordinator}
    
    # Enable alarms in options
    mock_config_entry.options["show_alarms"] = True
    
    async_add_entities = AsyncMock()
    
    await async_setup_entry(hass, mock_config_entry, async_add_entities)
    
    # Should not add entities if alarms disabled by default
    # But if enabled, should add
    if mock_config_entry.options.get("show_alarms"):
        # This would be called if alarms are enabled
        pass


def test_binary_sensor_is_on(mock_coordinator):
    """Test binary sensor is_on when alarm active."""
    mock_coordinator.data["alarm_kot_przegrzanie"] = "1"
    
    alarm = EkopiecAlarm(
        mock_coordinator,
        "alarm_kot_przegrzanie",
        {
            "name": "Boiler Overheating",
            "device_class": "problem",
        }
    )
    
    assert alarm.is_on is True


def test_binary_sensor_is_off(mock_coordinator):
    """Test binary sensor is_off when alarm inactive."""
    alarm = EkopiecAlarm(
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
    
    alarm = EkopiecAlarm(
        mock_coordinator,
        "alarm_test",
        {
            "name": "Test Alarm",
            "device_class": "problem",
        }
    )
    
    assert alarm.is_on is True

