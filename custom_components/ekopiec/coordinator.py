"""Data update coordinator for ekopiec."""
from datetime import timedelta
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
    
    async def set_parameter_with_limit(
        self, 
        parameter: str, 
        value: Any
    ) -> bool:
        """Set parameter with rate limiting."""
        # Check rate limit
        if not self._rate_limiter.should_allow():
            wait_time = self._rate_limiter.get_wait_time()
            _LOGGER.warning(
                "Rate limit active. Wait %.1f seconds before next request",
                wait_time
            )
            return False
        
        # Set parameter
        success = await self.api.set_parameter(parameter, value)
        
        if success:
            # Request refresh immediately
            await self.async_request_refresh()
        
        return success

