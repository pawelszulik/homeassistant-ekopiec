"""Tests for coordinator."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from homeassistant.core import HomeAssistant

from custom_components.ekopiec.coordinator import EkopiecDataUpdateCoordinator
from custom_components.ekopiec.api import ECoalApiClient, AuthenticationError
from homeassistant.helpers.update_coordinator import UpdateFailed


@pytest.mark.asyncio
async def test_update_data_success(hass: HomeAssistant, mock_api_client, sample_device_data):
    """Test successful data update."""
    mock_api_client.get_all_data = AsyncMock(return_value=sample_device_data)
    
    coordinator = EkopiecDataUpdateCoordinator(hass, mock_api_client)
    result = await coordinator._async_update_data()
    
    assert result is not None
    assert coordinator.device_info is not None
    assert coordinator.device_info["name"] == "Kocioł"
    # Check that timestamps were converted
    assert "add_fuel_time" in result
    assert "next_fuel_time" in result


@pytest.mark.asyncio
async def test_update_data_authentication_error(hass: HomeAssistant, mock_api_client):
    """Test update data with authentication error."""
    mock_api_client.get_all_data = AsyncMock(side_effect=AuthenticationError("Invalid credentials"))
    
    coordinator = EkopiecDataUpdateCoordinator(hass, mock_api_client)
    
    with pytest.raises(Exception):  # ConfigEntryAuthFailed
        await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_set_parameter_with_limit(hass: HomeAssistant, mock_api_client, sample_device_data):
    """Test set parameter with rate limiting."""
    mock_api_client.set_parameter = AsyncMock(return_value=True)
    
    coordinator = EkopiecDataUpdateCoordinator(hass, mock_api_client)
    coordinator.data = sample_device_data
    
    # First call should succeed
    result = await coordinator.set_parameter_with_limit("kot_tzad", 70.0)
    assert result is True
    
    # Second call immediately should be rate limited
    result = await coordinator.set_parameter_with_limit("kot_tzad", 75.0)
    assert result is False


@pytest.mark.asyncio
async def test_set_parameter_refresh(hass: HomeAssistant, mock_api_client, sample_device_data):
    """Test that set parameter triggers refresh."""
    mock_api_client.set_parameter = AsyncMock(return_value=True)
    
    coordinator = EkopiecDataUpdateCoordinator(hass, mock_api_client)
    coordinator.data = sample_device_data
    coordinator.async_request_refresh = AsyncMock()
    
    with patch("time.time", return_value=1000.0):
        result = await coordinator.set_parameter_with_limit("kot_tzad", 70.0)
    
    assert result is True
    coordinator.async_request_refresh.assert_called_once()


def test_convert_timestamps(hass: HomeAssistant, mock_api_client):
    """Test timestamp conversion."""
    coordinator = EkopiecDataUpdateCoordinator(hass, mock_api_client)
    
    data = {
        "add_fuel_time": "1731657600",
        "next_fuel_time": "1732262400",
    }
    
    coordinator._convert_timestamps(data)
    
    # Check that timestamps were converted to datetime strings
    assert data["add_fuel_time"] is not None
    assert isinstance(data["add_fuel_time"], str)
    assert "-" in data["add_fuel_time"]  # Should contain date separator
    assert ":" in data["add_fuel_time"]  # Should contain time separator
    
    assert data["next_fuel_time"] is not None
    assert isinstance(data["next_fuel_time"], str)
    assert "-" in data["next_fuel_time"]
    assert ":" in data["next_fuel_time"]


def test_convert_timestamps_invalid(hass: HomeAssistant, mock_api_client):
    """Test timestamp conversion with invalid data."""
    coordinator = EkopiecDataUpdateCoordinator(hass, mock_api_client)
    
    data = {
        "add_fuel_time": "invalid",
        "next_fuel_time": None,
    }
    
    coordinator._convert_timestamps(data)
    
    # Invalid timestamps should be set to None
    assert data["add_fuel_time"] is None
    assert data["next_fuel_time"] is None


@pytest.mark.asyncio
async def test_update_data_connection_error_preserves_data(hass: HomeAssistant, mock_api_client, sample_device_data):
    """Test that connection errors preserve previous data."""
    coordinator = EkopiecDataUpdateCoordinator(hass, mock_api_client)
    coordinator.data = sample_device_data  # Set previous data
    
    mock_api_client.get_all_data = AsyncMock(side_effect=ConnectionError("API timeout"))
    
    # Should return previous data instead of raising UpdateFailed
    result = await coordinator._async_update_data()
    
    assert result == sample_device_data
    assert result["device_sn"] == "AB123CD"


@pytest.mark.asyncio
async def test_update_data_connection_error_no_previous_data(hass: HomeAssistant, mock_api_client):
    """Test that connection errors raise UpdateFailed when no previous data."""
    coordinator = EkopiecDataUpdateCoordinator(hass, mock_api_client)
    coordinator.data = None  # No previous data
    
    mock_api_client.get_all_data = AsyncMock(side_effect=ConnectionError("API timeout"))
    
    # Should raise UpdateFailed when no previous data
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
