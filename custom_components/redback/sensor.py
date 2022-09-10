"""Redback sensors for the Redback integration."""
from __future__ import annotations

from homeassistant.core import (
    HomeAssistant,
    callback,
)
from homeassistant.config_entries import ConfigEntry

# from homeassistant.exceptions import ConfigEntryAuthFailed
# from homeassistant.helpers.aiohttp_client import async_get_clientsession
# from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

# , UpdateFailed

from homeassistant.const import (
    ELECTRIC_CURRENT_AMPERE,
    ELECTRIC_POTENTIAL_VOLT,
    ENERGY_KILO_WATT_HOUR,
    FREQUENCY_HERTZ,
    PERCENTAGE,
    POWER_KILO_WATT,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN, LOGGER
from .coordinator import RedbackDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup entities"""

    async_add_entities([RedbackChargeSensor(hass.data[DOMAIN][entry.entry_id])])


class RedbackChargeSensor(
    CoordinatorEntity[RedbackDataUpdateCoordinator], SensorEntity
):
    """Battery SoC (state of charge)"""

    coordinator: RedbackDataUpdateCoordinator
    _attr_name = "Battery SoC"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_value = 0.1

    def __init__(self, coordinator: RedbackDataUpdateCoordinator) -> None:
        """Pass coordinator to CoordinatorEntity."""
        self.coordinator = coordinator
        self._attr_unique_id = coordinator.config_entry.data["serial"] + "-soc"
        super().__init__(coordinator)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        LOGGER.info("Updating entity: %s", self._attr_unique_id)
        self._attr_native_value += 0.01
        self.async_write_ha_state()
