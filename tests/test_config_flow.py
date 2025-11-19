"""Tests for config flow."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.ekopiec.config_flow import EkopiecConfigFlow
from custom_components.ekopiec.api import AuthenticationError


@pytest.fixture
def flow(hass: HomeAssistant):
    """Create config flow."""
    return EkopiecConfigFlow()
    flow.hass = hass


@pytest.mark.asyncio
async def test_user_step_success(hass: HomeAssistant):
    """Test successful user step."""
    flow = EkopiecConfigFlow()
    flow.hass = hass
    
    with patch("custom_components.ekopiec.config_flow.ECoalApiClient") as mock_api:
        mock_instance = MagicMock()
        mock_instance.authenticate = AsyncMock(return_value={
            "device_sn": "AB123CD",
            "device_name": "Kocioł",
            "device_id": "5",
            "device_type": "eCoal",
        })
        mock_api.return_value = mock_instance
        
        result = await flow.async_step_user({
            "host": "192.168.1.100",
            "port": 80,
            "username": "test_user",
            "password": "test_pass",
        })
    
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Kocioł"
    assert result["data"]["host"] == "192.168.1.100"


@pytest.mark.asyncio
async def test_user_step_invalid_auth(hass: HomeAssistant):
    """Test user step with invalid auth."""
    flow = EkopiecConfigFlow()
    flow.hass = hass
    
    with patch("custom_components.ekopiec.config_flow.ECoalApiClient") as mock_api:
        mock_instance = MagicMock()
        mock_instance.authenticate = AsyncMock(side_effect=AuthenticationError("Invalid credentials"))
        mock_api.return_value = mock_instance
        
        result = await flow.async_step_user({
            "host": "192.168.1.100",
            "port": 80,
            "username": "test_user",
            "password": "wrong_pass",
        })
    
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "invalid_auth"


@pytest.mark.asyncio
async def test_user_step_cannot_connect(hass: HomeAssistant):
    """Test user step with connection error."""
    flow = EkopiecConfigFlow()
    flow.hass = hass
    
    with patch("custom_components.ekopiec.config_flow.ECoalApiClient") as mock_api:
        mock_instance = MagicMock()
        mock_instance.authenticate = AsyncMock(side_effect=ConnectionError("Connection failed"))
        mock_api.return_value = mock_instance
        
        result = await flow.async_step_user({
            "host": "192.168.1.100",
            "port": 80,
            "username": "test_user",
            "password": "test_pass",
        })
    
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "cannot_connect"



