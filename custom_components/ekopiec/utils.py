"""Utilities for ekopiec integration."""

import time
import logging
from typing import Optional

_LOGGER = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter to prevent API spam.
    
    Ensures minimum time interval between consecutive requests
    to protect the controller from being overwhelmed.
    """
    
    def __init__(self, min_interval: float = 2.0):
        """Initialize rate limiter.
        
        Args:
            min_interval: Minimum seconds between requests (default: 2)
        """
        self.min_interval = min_interval
        self._last_request: Optional[float] = None
    
    def should_allow(self) -> bool:
        """Check if request should be allowed.
        
        Returns:
            True if enough time has passed since last request
        """
        current_time = time.time()
        
        if self._last_request is None:
            # First request
            self._last_request = current_time
            return True
        
        elapsed = current_time - self._last_request
        if elapsed >= self.min_interval:
            # Enough time has passed
            self._last_request = current_time
            return True
        
        # Not enough time has passed
        return False
    
    def get_wait_time(self) -> float:
        """Get time to wait before next request.
        
        Returns:
            Seconds to wait (0.0 if ready)
        """
        if self._last_request is None:
            return 0.0
        
        elapsed = time.time() - self._last_request
        wait = self.min_interval - elapsed
        return max(0.0, wait)
    
    def reset(self) -> None:
        """Reset the rate limiter."""
        self._last_request = None

