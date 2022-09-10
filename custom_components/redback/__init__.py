"""The Redback Technologies Smart Hybrid integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry

# from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS, LOGGER
from .coordinator import RedbackDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up redback from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    # Data Update Coordinator
    # 1. calls into Redback API every SCAN_INTERVAL to download data
    # 2. calls each entity to update its own data
    coordinator = RedbackDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    LOGGER.info("New Redback integration setup (entry_id=%s)", entry.entry_id)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
