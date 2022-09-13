"""DataUpdateCoordinator for the Redback integration."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

# from homeassistant.exceptions import ConfigEntryAuthFailed

from .const import DOMAIN, LOGGER, SCAN_INTERVAL, TEST_MODE
from .redbacklib import RedbackInverter, TestRedbackInverter, RedbackError


class RedbackDataUpdateCoordinator(DataUpdateCoordinator):
    """The Redback Data Update Coordinator."""

    config_entry: ConfigEntry
    inverter_info: None
    energy_data: None

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the Redback coordinator."""
        self.config_entry = entry

        # RedbackInverter is the API connection to the Redback cloud portal
        if TEST_MODE:
            self.redback = TestRedbackInverter(
                cookie=entry.data["apikey"], serial=entry.data["serial"]
            )
        else:
            self.redback = RedbackInverter(
                cookie=entry.data["apikey"], serial=entry.data["serial"]
            )

        # these are the basic inverter details we always need
        self.inverter_info = self.redback.getInverterInfo()

        super().__init__(hass, LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Fetch system status from Redback."""
        LOGGER.debug(
            "Syncing data with Redback (entry_id=%s)", self.config_entry.entry_id
        )

        try:
            self.energy_data = self.redback.getEnergyData()
        except RedbackError as err:
            raise UpdateFailed("Redback API error: {err}") from err

        # try:
        #     return await self.pvoutput.status()
        # except PVOutputNoDataError as err:
        #     raise UpdateFailed("PVOutput has no data available") from err
        # except PVOutputAuthenticationError as err:
        #     raise ConfigEntryAuthFailed from err
