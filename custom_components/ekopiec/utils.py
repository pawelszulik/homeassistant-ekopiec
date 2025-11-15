"""Utility functions for ekopiec integration."""
import time
from typing import Optional


class RateLimiter:
    """Rate limiter to prevent API spam."""
    
    def __init__(self, min_interval: float = 2.0):
        """Initialize rate limiter.
        
        Args:
            min_interval: Minimum seconds between requests (default: 2)
        """
        self.min_interval = min_interval
        self._last_request: Optional[float] = None
    
    def should_allow(self) -> bool:
        """Check if request should be allowed."""
        current_time = time.time()
        
        if self._last_request is None:
            self._last_request = current_time
            return True
        
        elapsed = current_time - self._last_request
        if elapsed >= self.min_interval:
            self._last_request = current_time
            return True
        
        return False
    
    def get_wait_time(self) -> float:
        """Get time to wait before next request."""
        if self._last_request is None:
            return 0.0
        
        elapsed = time.time() - self._last_request
        wait = self.min_interval - elapsed
        return max(0.0, wait)

