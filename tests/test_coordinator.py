"""Tests for coordinator."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from homeassistant.core import HomeAssistant

from custom_components.ekopiec.coordinator import EkopiecDataUpdateCoordinator
from custom_components.ekopiec.api import ECoalApiClient, AuthenticationError


@pytest.mark.asyncio
async def test_update_data_success(hass: HomeAssistant, mock_api_client, sample_device_data):
    """Test successful data update."""
    mock_api_client.get_all_data = AsyncMock(return_value=sample_device_data)
    
    coordinator = EkopiecDataUpdateCoordinator(hass, mock_api_client)
    result = await coordinator._async_update_data()
    
    assert result == sample_device_data
    assert coordinator.device_info is not None
    assert coordinator.device_info["name"] == "Kocioł"


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

