"""DataUpdateCoordinator for the Redback integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry

# from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant

# from homeassistant.exceptions import ConfigEntryAuthFailed
# from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

# , UpdateFailed

from .const import DOMAIN, LOGGER, SCAN_INTERVAL


class RedbackDataUpdateCoordinator(DataUpdateCoordinator):
    """The Redback Data Update Coordinator."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the Redback coordinator."""
        self.config_entry = entry
        # self.pvoutput = PVOutput(
        #     api_key=entry.data[CONF_API_KEY],
        #     system_id=entry.data[CONF_SYSTEM_ID],
        #     session=async_get_clientsession(hass),
        # )

        super().__init__(hass, LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Fetch system status from Redback."""
        LOGGER.info(
            "Syncing data with Redback (entry_id=%s)", self.config_entry.entry_id
        )
        # try:
        #     return await self.pvoutput.status()
        # except PVOutputNoDataError as err:
        #     raise UpdateFailed("PVOutput has no data available") from err
        # except PVOutputAuthenticationError as err:
        #     raise ConfigEntryAuthFailed from err
