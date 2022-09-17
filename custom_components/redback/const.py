"""Constants for the redback integration."""

from homeassistant.const import Platform
from datetime import timedelta
import logging

DOMAIN = "redback"
PLATFORMS = [Platform.SENSOR]
TEST_MODE = True

LOGGER = logging.getLogger(__package__)
SCAN_INTERVAL = timedelta(minutes=1)

API_METHODS = [
    "private",
    "public",
]
