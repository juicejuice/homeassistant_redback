"""Provides diagnostics for Redback Technologies integration."""

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from .const import DOMAIN
from .coordinator import RedbackDataUpdateCoordinator

async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""

    payload = config_entry.as_dict()
    payload["data"]["auth"] = "***SECRET***"
    payload["data"]["client_id"] = "***SECRET***"

    return payload


async def async_get_device_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry, device: DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for a device entry."""

    coordinator: RedbackDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    updateInterval = (
        None
        if coordinator.update_interval is None
        else coordinator.update_interval.total_seconds()
    )

    return {
        "name": coordinator.name,
        "always_update": coordinator.always_update,
        "last_update_success": coordinator.last_update_success,
        "update_interval": updateInterval,
        "inverter_info": coordinator.inverter_info,
        "device_entry": device.dict_repr,
    }
