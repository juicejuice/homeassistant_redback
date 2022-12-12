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
        client_id = coordinator.config_entry.data["client_id"]
        self.coordinator = coordinator
        assert self.coordinator is not None
        super().__init__(coordinator)

        # store the base for the unique_id, to be used by each entity
        self.base_unique_id = client_id

        # some entities need these extra details
        if details:
            self._attr_name = details["name"]
            self.id_suffix = details["id_suffix"]
            self.data_source = details["data_source"]
            self.direction = details.get("direction")

        # link to the base Redback device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, client_id)},
            manufacturer="Redback Technologies",
            model=coordinator.inverter_info["Model"]
            + " "
            + coordinator.inverter_info["ProductDisplayname"],
            name=coordinator.config_entry.data["displayname"],
            sw_version=coordinator.inverter_info["Firmware"],
            configuration_url="https://portal.redbacktech.com/",
        )
