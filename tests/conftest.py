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
        # Temperature sensors
        "tkot_value": "65.5",
        "tpow_value": "42.3",
        "tpod_value": "35.0",
        "tcwu_value": "55.2",
        "tsp_value": "150.0",
        # Blower sensors
        "dm_rms": "75",
        "act_dm_speed": "80",
        # Regulator parameters
        "rr_g_pod_off": "60",
        "rr_g_pod_on": "10",
        "rr_rsp_dm_speed": "30",
        "rr_rsp_tmax": "200",
        "rr_rsp_en": "1",
        "rr_g_dm_speed": "50",
        # Setpoints
        "kot_tzad": "70.0",
        "cwu_tzad": "60.0",
        "pomp_ton": "45.0",
        "tpow_min": "40.0",
        # Feeder parameters
        "p_pod_on": "15",
        "p_pod_off": "120",
        "p_pod_wait": "5",
        "p_pod_cnt": "3",
        # Operating modes
        "zima_lato": "0",
        "tryb_auto_state": "1",
        # Fuel sensors
        "fuel_level": "75",
        "pod_run_time_str": "120:45:30",
        # Valve position
        "ob1_zaw4d_pos": "50",
        # Date/Time
        "datetime": "2025-11-17T22:45:33Z",
        "add_fuel_time": "1731657600",
        "next_fuel_time": "1732262400",
        # Output status
        "out_pomp1": "1",
        "out_cwu": "0",
        "out_miesz": "0",
        "out_dm": "1",
        # Alarms
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
    entry.options = {}
    return entry
