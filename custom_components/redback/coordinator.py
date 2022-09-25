"""DataUpdateCoordinator for the Redback integration."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from homeassistant.helpers.aiohttp_client import async_get_clientsession
# from homeassistant.exceptions import ConfigEntryAuthFailed

from .const import DOMAIN, LOGGER, SCAN_INTERVAL, TEST_MODE
from .redbacklib import RedbackInverter, TestRedbackInverter, RedbackError, RedbackAPIError


class RedbackDataUpdateCoordinator(DataUpdateCoordinator):
    """The Redback Data Update Coordinator."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the Redback coordinator."""
        self.config_entry = entry
        clientsession = async_get_clientsession(hass)

        # RedbackInverter is the API connection to the Redback cloud portal
        if TEST_MODE:
            self.redback = TestRedbackInverter(
                cookie=entry.data["apikey"], serial=entry.data["serial"], apimethod=entry.data["apimethod"], session=clientsession
            )
        else:
            self.redback = RedbackInverter(
                cookie=entry.data["apikey"], serial=entry.data["serial"], apimethod=entry.data["apimethod"], session=clientsession
            )

        super().__init__(hass, LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Fetch system status from Redback."""
        LOGGER.debug(
            "Syncing data with Redback (entry_id=%s)", self.config_entry.entry_id
        )

        try:
            if (not hasattr(self, "inverter_info")):
                self.inverter_info = await self.redback.getInverterInfo()
            self.energy_data = await self.redback.getEnergyData()
        except RedbackError as err:
            raise UpdateFailed("Connection error: {err}") from err
        except RedbackAPIError as err:
            raise UpdateFailed("API error: {err}") from err

        return self.energy_data

