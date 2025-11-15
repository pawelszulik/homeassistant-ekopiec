"""Constants for the ekopiec integration."""
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfTime,
)

DOMAIN = "ekopiec"

# Configuration
CONF_PORT = "port"
DEFAULT_PORT = 80
DEFAULT_SCAN_INTERVAL = 30
HEATING_CIRCUITS = 6

# API Timeouts
API_TIMEOUT = 15

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 1

# Rate limiting
MIN_REQUEST_INTERVAL = 2.0

