"""Redback entity base class for the Redback integration."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RedbackDataUpdateCoordinator


class RedbackEntity(CoordinatorEntity[RedbackDataUpdateCoordinator]):
    """Base class for Redback entities"""

    coordinator: RedbackDataUpdateCoordinator
    _attr_has_entity_name = True

    def __init__(self, coordinator: RedbackDataUpdateCoordinator, details) -> None:
        # initialise the entity
        site_id = coordinator.config_entry.data["site_id"]
        self.coordinator = coordinator
        assert self.coordinator is not None
        super().__init__(coordinator)

        # store the base for the unique_id, to be used by each entity
        self.base_unique_id = site_id

        # some entities need these extra details
        if details:
            self._attr_name = details["name"]
            self.id_suffix = details["id_suffix"]
            self.data_source = details["data_source"]
            self.direction = details.get("direction")
            self.convertPercent = details.get("convertPercent")
            self.convertkW = details.get("convertkW")

        # link to the base Redback device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, site_id)},
            manufacturer="Redback Technologies",
            model=coordinator.inverter_info["ModelName"],
            name=coordinator.config_entry.data["displayname"],
            sw_version=coordinator.inverter_info["FirmwareVersion"],
            configuration_url="https://portal.redbacktech.com/",
        )
