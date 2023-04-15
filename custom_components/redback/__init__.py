"""The Redback Technologies cloud portal integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS, LOGGER
from .coordinator import RedbackDataUpdateCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Redback from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    # Data Update Coordinator
    # 1. calls into Redback API every SCAN_INTERVAL to download and refresh data cache
    # 2. then calls each entity to update its own data from cache
    coordinator = RedbackDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    LOGGER.debug("New Redback integration is setup (entry_id=%s)", entry.entry_id)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Redback config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def async_migrate_entry(hass, entry: ConfigEntry):
    """Migrate outdated Redback config entry."""
    LOGGER.debug("Migrating config entry from version %s", entry.version)

    # migrate version 1 to 2
    if entry.version == 1:
        new = {**entry.data}
        # in version 1, the client_id was used for unique_ids for entities, in version 2 we use site_id instead,
        # therefore, for migration purposes we bring client_id over to site_id to avoid creating all new entities
        new["site_id"] = new["client_id"]
        new["site_index"] = "First"
        entry.version = 2

        hass.config_entries.async_update_entry(entry, data=new)

    LOGGER.info("Successful migration of config entry to version %s", entry.version)

    return True
