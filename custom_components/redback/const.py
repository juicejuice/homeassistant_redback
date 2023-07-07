"""Constants for the redback integration."""

from homeassistant.const import Platform
from datetime import timedelta
import logging

DOMAIN = "redback"
PLATFORMS = [Platform.SENSOR]
TEST_MODE = False

LOGGER = logging.getLogger(__package__)
SCAN_INTERVAL = timedelta(minutes=1)

API_METHODS = [
    "public",
    "private",
]

INVERTER_MODES = ["NoMode", "Auto", "ChargeBattery", "DischargeBattery", "ImportPower", "ExportPower", "Conserve", "Offgrid", "Hibernate", "BuyPower", "SellPower", "ForceChargeBattery", "ForceDischargeBattery", "Stop"]
INVERTER_STATUS = ["OK", "Offline", "Fault"]
