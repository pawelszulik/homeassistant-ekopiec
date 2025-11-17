"""Data update coordinator for ekopiec."""
from datetime import timedelta, datetime
import logging
from typing import Any, Dict

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed

from .api import ECoalApiClient, AuthenticationError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, MIN_REQUEST_INTERVAL
from .utils import RateLimiter

_LOGGER = logging.getLogger(__name__)


class EkopiecDataUpdateCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Class to manage fetching ekopiec data."""
    
    def __init__(
        self, 
        hass: HomeAssistant, 
        api: ECoalApiClient,
        update_interval: int = DEFAULT_SCAN_INTERVAL
    ):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="ekopiec",
            update_interval=timedelta(seconds=update_interval),
        )
        self.api = api
        self.device_info = None
        self._rate_limiter = RateLimiter(min_interval=MIN_REQUEST_INTERVAL)
        
    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from API."""
        try:
            data = await self.api.get_all_data()
            
            # Convert Unix timestamps to datetime strings
            self._convert_timestamps(data)
            
            # Store device info on first update
            if self.device_info is None:
                self.device_info = {
                    "identifiers": {(DOMAIN, data.get("device_sn"))},
                    "name": data.get("device_name", "ekopiec"),
                    "manufacturer": "eSterownik.pl",
                    "model": data.get("device_type"),
                    "sw_version": data.get("device_soft_version"),
                    "hw_version": data.get("device_hard_version"),
                }
            
            return data
            
        except AuthenticationError as err:
            raise ConfigEntryAuthFailed("Authentication failed") from err
        except Exception as err:
            raise UpdateFailed(f"Error communicating with controller: {err}") from err
    
    def _convert_timestamps(self, data: Dict[str, Any]) -> None:
        """Convert Unix timestamps to ISO datetime strings.
        
        Converts timestamps for:
        - add_fuel_time: Last fuel refill timestamp
        - next_fuel_time: Next fuel refill timestamp
        - datetime: Current date/time from controller
        
        Args:
            data: Device data dictionary to update with converted values
        """
        # Unix timestamp fields (need conversion from seconds)
        timestamp_fields = ["add_fuel_time", "next_fuel_time"]
        
        for field in timestamp_fields:
            timestamp_value = data.get(field)
            
            if timestamp_value is None:
                continue
            
            try:
                # Convert Unix timestamp (seconds) to datetime string
                if isinstance(timestamp_value, str) and timestamp_value.isdigit():
                    timestamp = int(timestamp_value)
                elif isinstance(timestamp_value, (int, float)):
                    timestamp = int(timestamp_value)
                else:
                    _LOGGER.debug("Skipping non-numeric timestamp for %s: %s", field, timestamp_value)
                    continue
                
                # Convert to datetime and format as ISO string (YYYY-MM-DDTHH:MM:SS)
                dt = datetime.fromtimestamp(timestamp)
                data[field] = dt.isoformat()
                
                _LOGGER.debug(
                    "Converted %s: %s -> %s",
                    field, timestamp, data[field]
                )
                
            except (ValueError, OSError, OverflowError) as err:
                _LOGGER.warning("Cannot convert timestamp for %s (%s): %s", field, timestamp_value, err)
                data[field] = None
        
        # datetime field is already in ISO format (2025-11-17T22:45:33Z), just validate it
        datetime_value = data.get("datetime")
        if datetime_value and isinstance(datetime_value, str):
            # Remove 'Z' suffix if present and ensure it's valid
            if datetime_value.endswith('Z'):
                data["datetime"] = datetime_value[:-1]
            _LOGGER.debug("Datetime field: %s", data["datetime"])
    
    async def set_parameter_with_limit(
        self, 
        parameter: str, 
        value: Any
    ) -> bool:
        """Set parameter with rate limiting.
        
        Args:
            parameter: Parameter name
            value: Value to set
            
        Returns:
            True if successful, False if rate limited
        """
        # Check rate limit
        if not self._rate_limiter.should_allow():
            wait_time = self._rate_limiter.get_wait_time()
            _LOGGER.warning(
                "Rate limit active. Wait %.1f seconds before next request.",
                wait_time
            )
            return False
        
        # Set parameter
        success = await self.api.set_parameter(parameter, value)
        
        if success:
            # Request refresh immediately after successful set
            await self.async_request_refresh()
        
        return success
