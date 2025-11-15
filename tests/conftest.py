"""Pytest configuration and fixtures."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from custom_components.ekopiec.api import ECoalApiClient
from custom_components.ekopiec.coordinator import EkopiecDataUpdateCoordinator


@pytest.fixture
def mock_api_client():
    """Create a mock API client."""
    client = MagicMock(spec=ECoalApiClient)
    client.host = "192.168.1.100"
    client.port = 80
    client.username = "test_user"
    client.password = "test_pass"
    client.base_url = "http://192.168.1.100:80"
    return client


@pytest.fixture
def sample_device_data():
    """Sample device data from API."""
    return {
        "readed_date": "1731657600",
        "device_sn": "AB123CD",
        "device_id": "5",
        "device_name": "Kocioł",
        "device_type": "eCoal",
        "device_soft_version": "1.0.0",
        "device_hard_version": "2.0",
        "kot_value": "65.5",
        "kot_tzad": "70.0",
        "tpow_value": "42.3",
        "tcwu_value": "55.2",
        "tcwu_tzad": "60.0",
        "ob1_typ": "1",
        "ob1_temp": "45.0",
        "ob1_tzad": "50.0",
        "ob1_tryb": "1",
        "pompa_kotla": "1",
        "pompa_cwu": "0",
        "dmuchawa": "1",
        "paliwo_poziom": "75",
        "paliwo_czas_pracy": "120",
        "alarm_kot_przegrzanie": "0",
        "alarm_paliwo_brak": "0",
    }


@pytest.fixture
def mock_coordinator(hass: HomeAssistant, mock_api_client, sample_device_data):
    """Create a mock coordinator."""
    coordinator = EkopiecDataUpdateCoordinator(hass, mock_api_client)
    coordinator.data = sample_device_data
    coordinator.device_info = {
        "identifiers": {("ekopiec", "AB123CD")},
        "name": "Kocioł",
        "manufacturer": "eSterownik.pl",
        "model": "eCoal",
    }
    return coordinator


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry_id"
    entry.data = {
        "host": "192.168.1.100",
        "port": 80,
        "username": "test_user",
        "password": "test_pass",
    }
    entry.options = {
        "show_temperatures": True,
        "show_climate": True,
        "show_dhw": True,
        "show_switches": True,
        "show_fuel": True,
        "show_alarms": False,
        "show_numbers": True,
    }
    return entry

