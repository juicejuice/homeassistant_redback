"""Redback sensors for the Redback integration."""
from __future__ import annotations

from datetime import (datetime, timedelta)
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

from .const import DOMAIN, LOGGER
from .entity import RedbackEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup entities"""

    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            RedbackChargeSensor(coordinator, None),
            RedbackPowerSensor(
                coordinator,
                {
                    "name": "Load Power",
                    "id_suffix": "load_power",
                    "data_source": "ACLoadW",
                },
            ),
            RedbackPowerSensor(
                coordinator,
                {
                    "name": "Backup Load Power",
                    "id_suffix": "backup_load_power",
                    "data_source": "BackupLoadW",
                },
            ),
            RedbackPowerSensor(
                coordinator,
                {
                    "name": "Solar Power",
                    "id_suffix": "solar_power",
                    "data_source": "PVW",
                },
            ),
            RedbackPowerSensor(
                coordinator,
                {
                    "name": "Battery Power",
                    "id_suffix": "battery_power",
                    "data_source": "BatteryNegativeIsChargingW",
                },
            ),
            RedbackPowerSensor(
                coordinator,
                {
                    "name": "Grid Power",
                    "id_suffix": "grid_power",
                    "data_source": "GridNegativeIsImportW",
                },
            ),
            RedbackEnergySensor(
                coordinator,
                {
                    "name": "Grid Export",
                    "id_suffix": "grid_export",
                    "data_source": "GridNegativeIsImportW",
                    "direction": "positive",
                },
            ),
            RedbackEnergySensor(
                coordinator,
                {
                    "name": "Grid Import",
                    "id_suffix": "grid_import",
                    "data_source": "GridNegativeIsImportW",
                    "direction": "negative",
                },
            ),
            RedbackEnergySensor(
                coordinator,
                {
                    "name": "Solar Generation",
                    "id_suffix": "solar_gen",
                    "data_source": "PVW",
                    "direction": "positive",
                },
            ),
            RedbackEnergySensor(
                coordinator,
                {
                    "name": "Battery Charge",
                    "id_suffix": "battery_charge",
                    "data_source": "BatteryNegativeIsChargingW",
                    "direction": "negative",
                },
            ),
            RedbackEnergySensor(
                coordinator,
                {
                    "name": "Battery Discharge",
                    "id_suffix": "battery_discharge",
                    "data_source": "BatteryNegativeIsChargingW",
                    "direction": "positive",
                },
            ),
            RedbackEnergySensor(
                coordinator,
                {
                    "name": "Load Energy",
                    "id_suffix": "load_energy",
                    "data_source": "ACLoadW",
                    "direction": "positive",
                },
            ),
            RedbackEnergySensor(
                coordinator,
                {
                    "name": "Backup Load Energy",
                    "id_suffix": "backup_load_energy",
                    "data_source": "BackupLoadW",
                    "direction": "positive",
                },
            ),
        ]
    )


class RedbackChargeSensor(RedbackEntity, SensorEntity):
    """Sensor for battery state-of-charge"""

    _attr_name = "Battery Charge"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.BATTERY

    @property
    def unique_id(self) -> str:
        """Device Uniqueid."""
        return f"{self.base_unique_id}_charge"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        LOGGER.debug("Updating entity: %s", self.unique_id)
        self._attr_native_value = self.coordinator.energy_data["BatterySoC0to100"]
        self.async_write_ha_state()


class RedbackPowerSensor(RedbackEntity, SensorEntity):
    """Sensor for power"""

    _attr_name = "Power"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = POWER_KILO_WATT
    _attr_device_class = SensorDeviceClass.POWER

    @property
    def unique_id(self) -> str:
        """Device Uniqueid."""
        return f"{self.base_unique_id}_{self.id_suffix}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        LOGGER.debug("Updating entity: %s", self.unique_id)
        self._attr_native_value = self.coordinator.energy_data[self.data_source]
        self.async_write_ha_state()

class RedbackEnergySensor(RedbackEntity, SensorEntity):
    """Sensor for testing"""

    _attr_name = "Energy"
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY

    @property
    def unique_id(self) -> str:
        """Device Uniqueid."""
        return f"{self.base_unique_id}_{self.id_suffix}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        LOGGER.debug("Updating entity: %s", self.unique_id)
        measurement = self.coordinator.energy_data[self.data_source]
        if(self.direction == "positive"):
            measurement = max(measurement, 0)
        else:
            measurement = min(measurement, 0)
        self._attr_native_value = measurement / 60000 # convert from W to kWh (sampling resolution is 60s)
        self._attr_last_reset = datetime.now() - timedelta(minutes=1)
        self.async_write_ha_state()
