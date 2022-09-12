"""Redback entity base class for the Redback integration."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RedbackDataUpdateCoordinator


class RedbackEntity(CoordinatorEntity[RedbackDataUpdateCoordinator]):
    """Base class for Redback entities"""

    coordinator: RedbackDataUpdateCoordinator

    def __init__(self, coordinator: RedbackDataUpdateCoordinator) -> None:
        """Pass coordinator to CoordinatorEntity."""
        serial = coordinator.config_entry.data["serial"]
        self.coordinator = coordinator
        assert self.coordinator is not None
        super().__init__(coordinator)
        self.base_unique_id = serial
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer="Redback Technologies",
            model=coordinator.inverter_info["Model"],
            name=coordinator.inverter_info["ProductDisplayname"],
            sw_version=coordinator.inverter_info["Firmware"],
            configuration_url="https://portal.redbacktech.com/",
        )
