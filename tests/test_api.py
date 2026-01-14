"""Tests for API client."""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp
import xml.etree.ElementTree as ET

from custom_components.ekopiec.api import ECoalApiClient, AuthenticationError


@pytest.fixture
def api_client():
    """Create API client instance."""
    session = MagicMock(spec=aiohttp.ClientSession)
    return ECoalApiClient(
        host="192.168.1.100",
        username="test_user",
        password="test_pass",
        port=80,
        session=session,
    )


def test_decode_syncvalues(api_client):
    """Test decoding syncvalues format."""
    raw_data = "1731657600;device_sn:AB123CD;device_id:5;tkot_value:65.5;tpow_value:42.3"
    result = api_client._decode_syncvalues(raw_data)
    
    assert result["readed_date"] == "1731657600"
    assert result["device_sn"] == "AB123CD"
    assert result["device_id"] == "5"
    assert result["tkot_value"] == "65.5"
    assert result["tpow_value"] == "42.3"


def test_decode_syncvalues_with_encoding(api_client):
    """Test decoding with special encoding."""
    raw_data = "1731657600;test_key:value%2with%2commas;other_key:value%3Dequals"
    result = api_client._decode_syncvalues(raw_data)
    
    assert result["test_key"] == "value,with,commas"
    assert result["other_key"] == "value=equals"


def test_decode_syncvalues_empty(api_client):
    """Test decoding empty data."""
    result = api_client._decode_syncvalues("")
    assert result == {}


@pytest.mark.asyncio
async def test_get_all_data_success(api_client):
    """Test successful get_all_data."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text = AsyncMock(return_value="1731657600;device_sn:AB123CD;tkot_value:65.5")
    mock_response.json = AsyncMock()
    
    # Create proper async context manager for session.get
    mock_get_context = AsyncMock()
    mock_get_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_get_context.__aexit__ = AsyncMock(return_value=None)
    api_client._session.get = MagicMock(return_value=mock_get_context)
    
    # Mock async_timeout.timeout as async context manager
    mock_timeout = MagicMock()
    mock_timeout.__aenter__ = AsyncMock(return_value=None)
    mock_timeout.__aexit__ = AsyncMock(return_value=None)
    
    with patch("custom_components.ekopiec.api.async_timeout.timeout", return_value=mock_timeout):
        result = await api_client.get_all_data()
    
    assert result["device_sn"] == "AB123CD"
    assert result["tkot_value"] == "65.5"


@pytest.mark.asyncio
async def test_get_all_data_authentication_error(api_client):
    """Test authentication error."""
    mock_response = AsyncMock()
    mock_response.status = 401
    
    # Create proper async context manager for session.get
    mock_get_context = AsyncMock()
    mock_get_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_get_context.__aexit__ = AsyncMock(return_value=None)
    api_client._session.get = MagicMock(return_value=mock_get_context)
    
    # Mock async_timeout.timeout as async context manager
    mock_timeout = MagicMock()
    mock_timeout.__aenter__ = AsyncMock(return_value=None)
    mock_timeout.__aexit__ = AsyncMock(return_value=None)
    
    with patch("custom_components.ekopiec.api.async_timeout.timeout", return_value=mock_timeout):
        with pytest.raises(AuthenticationError):
            await api_client.get_all_data()


@pytest.mark.asyncio
async def test_set_parameter_success(api_client):
    """Test successful set_parameter."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text = AsyncMock(return_value="<cmd status='ok'></cmd>")
    
    # Create proper async context manager for session.get
    mock_get_context = AsyncMock()
    mock_get_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_get_context.__aexit__ = AsyncMock(return_value=None)
    api_client._session.get = MagicMock(return_value=mock_get_context)
    
    # Mock async_timeout.timeout as async context manager
    mock_timeout = MagicMock()
    mock_timeout.__aenter__ = AsyncMock(return_value=None)
    mock_timeout.__aexit__ = AsyncMock(return_value=None)
    
    with patch("custom_components.ekopiec.api.async_timeout.timeout", return_value=mock_timeout):
        result = await api_client.set_parameter("kot_tzad", 70.0)
    
    assert result is True


@pytest.mark.asyncio
async def test_set_parameter_error(api_client):
    """Test set_parameter with error response."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text = AsyncMock(return_value="<cmd status='error'></cmd>")
    
    # Create proper async context manager for session.get
    mock_get_context = AsyncMock()
    mock_get_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_get_context.__aexit__ = AsyncMock(return_value=None)
    api_client._session.get = MagicMock(return_value=mock_get_context)
    
    # Mock async_timeout.timeout as async context manager
    mock_timeout = MagicMock()
    mock_timeout.__aenter__ = AsyncMock(return_value=None)
    mock_timeout.__aexit__ = AsyncMock(return_value=None)
    
    with patch("custom_components.ekopiec.api.async_timeout.timeout", return_value=mock_timeout):
        result = await api_client.set_parameter("kot_tzad", 70.0)
    
    assert result is False


@pytest.mark.asyncio
async def test_set_parameter_retry(api_client):
    """Test set_parameter retry logic."""
    # First call fails, second succeeds
    mock_response_error = AsyncMock()
    mock_response_error.status = 200
    mock_response_error.text = AsyncMock(return_value="<cmd status='error'></cmd>")
    
    mock_response_ok = AsyncMock()
    mock_response_ok.status = 200
    mock_response_ok.text = AsyncMock(return_value="<cmd status='ok'></cmd>")
    
    # Create proper async context managers for session.get
    mock_get_context_1 = AsyncMock()
    mock_get_context_1.__aenter__ = AsyncMock(return_value=mock_response_error)
    mock_get_context_1.__aexit__ = AsyncMock(return_value=None)
    
    mock_get_context_2 = AsyncMock()
    mock_get_context_2.__aenter__ = AsyncMock(return_value=mock_response_ok)
    mock_get_context_2.__aexit__ = AsyncMock(return_value=None)
    
    api_client._session.get = MagicMock(side_effect=[mock_get_context_1, mock_get_context_2])
    
    # Mock async_timeout.timeout as async context manager
    mock_timeout = MagicMock()
    mock_timeout.__aenter__ = AsyncMock(return_value=None)
    mock_timeout.__aexit__ = AsyncMock(return_value=None)
    
    with patch("custom_components.ekopiec.api.async_timeout.timeout", return_value=mock_timeout):
        with patch("asyncio.sleep"):
            result = await api_client.set_parameter("kot_tzad", 70.0)
    
    assert result is True
    assert api_client._session.get.call_count == 2


@pytest.mark.asyncio
async def test_get_all_data_retry_on_timeout(api_client):
    """Test get_all_data retry logic on timeout."""
    # First call times out, second succeeds
    mock_response_ok = AsyncMock()
    mock_response_ok.status = 200
    mock_response_ok.text = AsyncMock(return_value="1731657600;device_sn:AB123CD;tkot_value:65.5")
    mock_response_ok.json = AsyncMock()
    
    # Create proper async context manager for session.get (only second call succeeds)
    mock_get_context = AsyncMock()
    mock_get_context.__aenter__ = AsyncMock(return_value=mock_response_ok)
    mock_get_context.__aexit__ = AsyncMock(return_value=None)
    api_client._session.get = MagicMock(return_value=mock_get_context)
    
    # Mock timeout on first call (timeout occurs in __aenter__), success on second
    # When timeout occurs, _session.get is not called, so we only expect 1 call
    timeout_context_1 = MagicMock()
    timeout_context_1.__aenter__ = AsyncMock(side_effect=asyncio.TimeoutError())
    timeout_context_1.__aexit__ = AsyncMock(return_value=None)
    
    timeout_context_2 = MagicMock()
    timeout_context_2.__aenter__ = AsyncMock(return_value=None)
    timeout_context_2.__aexit__ = AsyncMock(return_value=None)
    
    with patch("custom_components.ekopiec.api.async_timeout.timeout", side_effect=[timeout_context_1, timeout_context_2]):
        with patch("asyncio.sleep"):
            result = await api_client.get_all_data()
    
    assert result["device_sn"] == "AB123CD"
    # When timeout occurs in __aenter__, _session.get is not called in first attempt
    # So we expect only 1 call (second attempt succeeds)
    assert api_client._session.get.call_count == 1


@pytest.mark.asyncio
async def test_get_all_data_retry_on_connection_error(api_client):
    """Test get_all_data retry logic on connection error."""
    # First call fails with connection error, second succeeds
    mock_response_ok = AsyncMock()
    mock_response_ok.status = 200
    mock_response_ok.text = AsyncMock(return_value="1731657600;device_sn:AB123CD;tkot_value:65.5")
    mock_response_ok.json = AsyncMock()
    
    # Create proper async context managers for session.get
    mock_get_context_1 = AsyncMock()
    mock_get_context_1.__aenter__ = AsyncMock(side_effect=aiohttp.ClientError("Connection failed"))
    mock_get_context_1.__aexit__ = AsyncMock(return_value=None)
    
    mock_get_context_2 = AsyncMock()
    mock_get_context_2.__aenter__ = AsyncMock(return_value=mock_response_ok)
    mock_get_context_2.__aexit__ = AsyncMock(return_value=None)
    
    api_client._session.get = MagicMock(side_effect=[mock_get_context_1, mock_get_context_2])
    
    # Mock async_timeout.timeout as async context manager
    mock_timeout = MagicMock()
    mock_timeout.__aenter__ = AsyncMock(return_value=None)
    mock_timeout.__aexit__ = AsyncMock(return_value=None)
    
    with patch("custom_components.ekopiec.api.async_timeout.timeout", return_value=mock_timeout):
        with patch("asyncio.sleep"):
            result = await api_client.get_all_data()
    
    assert result["device_sn"] == "AB123CD"
    assert api_client._session.get.call_count == 2
