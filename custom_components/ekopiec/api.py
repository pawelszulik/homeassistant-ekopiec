"""API Client for eCoal controller."""
import asyncio
import logging
import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional

import aiohttp
import async_timeout

_LOGGER = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Authentication error."""
    pass


class ECoalApiClient:
    """API Client for eCoal controller."""
    
    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 80,
        session: Optional[aiohttp.ClientSession] = None
    ):
        """Initialize the API client."""
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self._session = session
        self._auth = aiohttp.BasicAuth(username, password)
    
    @property
    def base_url(self) -> str:
        """Return base URL."""
        return f"http://{self.host}:{self.port}"
    
    def _decode_syncvalues(self, raw_data: str) -> Dict[str, Any]:
        """Decode custom format from /syncvalues.cgi to dictionary."""
        try:
            result = {}
            segments = raw_data.split("\r")
            segments = [s for s in segments if len(s) > 1]
            
            if not segments:
                return result
            
            first_segment = segments[0]
            records = first_segment.split(";")
            records = [r for r in records if len(r) > 1]
            
            if records:
                result["readed_date"] = records[0]
            
            for record in records[1:]:
                if ":" in record:
                    key, value = record.split(":", 1)
                    value = value.replace("%2", ",").replace("%3D", "=")
                    result[key] = value
            
            return result
        except Exception as e:
            _LOGGER.error("Error decoding data: %s", e)
            return {}
    
    async def authenticate(self) -> Dict[str, Any]:
        """Test connection and return device info."""
        try:
            data = await self.get_all_data()
            return {
                "device_id": data.get("device_id"),
                "device_sn": data.get("device_sn"),
                "device_name": data.get("device_name"),
                "device_type": data.get("device_type"),
            }
        except Exception as e:
            _LOGGER.error("Authentication failed: %s", e)
            raise
    
    async def get_all_data(self) -> Dict[str, Any]:
        """Fetch all data from /syncvalues.cgi endpoint."""
        url = f"{self.base_url}/syncvalues.cgi"
        
        if self._session is None:
            raise RuntimeError("Session not initialized")
        
        try:
            async with async_timeout.timeout(15):
                async with self._session.get(url, auth=self._auth) as response:
                    if response.status == 401:
                        raise AuthenticationError("Invalid credentials")
                    
                    if response.status == 200:
                        content = await response.text()
                        
                        # Try JSON first, then decode custom format
                        if content.strip().startswith("{"):
                            return await response.json()
                        else:
                            return self._decode_syncvalues(content)
                    else:
                        raise ConnectionError(f"HTTP {response.status}")
        
        except asyncio.TimeoutError as err:
            raise ConnectionError("API timeout") from err
        except aiohttp.ClientError as err:
            raise ConnectionError(f"Connection error: {err}") from err
    
    async def set_parameter(self, parameter: str, value: Any) -> bool:
        """Set parameter via /setregister.cgi?device=0&property=value
        
        Response is XML: <cmd status='ok'></cmd>
        Includes retry logic and validation.
        """
        url = f"{self.base_url}/setregister.cgi"
        params = {"device": "0", parameter: str(value)}
        
        if self._session is None:
            raise RuntimeError("Session not initialized")
        
        # Retry logic - up to 3 attempts
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                async with async_timeout.timeout(15):
                    async with self._session.get(
                        url,
                        params=params,
                        auth=self._auth
                    ) as response:
                        if response.status == 401:
                            raise AuthenticationError("Invalid credentials")
                        
                        if response.status == 200:
                            content = await response.text()
                            
                            try:
                                # Parse XML response
                                root = ET.fromstring(content)
                                status = root.get('status')
                                
                                if status and status.lower() == 'ok':
                                    _LOGGER.debug(
                                        "Set %s=%s success",
                                        parameter, value
                                    )
                                    return True
                                else:
                                    _LOGGER.warning(
                                        "Set %s=%s failed: status=%s (retry %d/%d)",
                                        parameter, value, status, retry_count + 1, max_retries
                                    )
                                    retry_count += 1
                                    if retry_count < max_retries:
                                        await asyncio.sleep(1)  # Wait before retry
                                    continue
                            except ET.ParseError as e:
                                _LOGGER.error("XML parse error: %s (retry %d/%d)", e, retry_count + 1, max_retries)
                                retry_count += 1
                                if retry_count < max_retries:
                                    await asyncio.sleep(1)
                                continue
                        else:
                            _LOGGER.warning("HTTP %s (retry %d/%d)", response.status, retry_count + 1, max_retries)
                            retry_count += 1
                            if retry_count < max_retries:
                                await asyncio.sleep(1)
                            continue
            
            except asyncio.TimeoutError as err:
                _LOGGER.warning("Timeout setting %s (retry %d/%d)", parameter, retry_count + 1, max_retries)
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(1)
                continue
            except aiohttp.ClientError as err:
                _LOGGER.warning("Connection error: %s (retry %d/%d)", err, retry_count + 1, max_retries)
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(1)
                continue
        
        _LOGGER.error("Failed to set %s after %d retries", parameter, max_retries)
        return False

