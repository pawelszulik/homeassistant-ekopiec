"""Tests for utility functions."""
import pytest
import time
from unittest.mock import patch

from custom_components.ekopiec.utils import RateLimiter


def test_rate_limiter_first_request():
    """Test rate limiter allows first request."""
    limiter = RateLimiter(min_interval=2.0)
    assert limiter.should_allow() is True


def test_rate_limiter_too_soon():
    """Test rate limiter blocks request too soon."""
    limiter = RateLimiter(min_interval=2.0)
    
    with patch("time.time", return_value=1000.0):
        assert limiter.should_allow() is True
    
    with patch("time.time", return_value=1000.5):
        assert limiter.should_allow() is False


def test_rate_limiter_after_interval():
    """Test rate limiter allows request after interval."""
    limiter = RateLimiter(min_interval=2.0)
    
    with patch("time.time", return_value=1000.0):
        assert limiter.should_allow() is True
    
    with patch("time.time", return_value=1002.0):
        assert limiter.should_allow() is True


def test_get_wait_time():
    """Test get wait time calculation."""
    limiter = RateLimiter(min_interval=2.0)
    
    with patch("time.time", return_value=1000.0):
        limiter.should_allow()
    
    with patch("time.time", return_value=1000.5):
        wait_time = limiter.get_wait_time()
        assert wait_time == pytest.approx(1.5, abs=0.1)


def test_get_wait_time_none():
    """Test get wait time when no previous request."""
    limiter = RateLimiter(min_interval=2.0)
    assert limiter.get_wait_time() == 0.0

