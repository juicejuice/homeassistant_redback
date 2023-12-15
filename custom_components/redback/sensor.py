"""Redback sensors for the Redback integration."""
from __future__ import annotations

from datetime import (datetime, timedelta)
from homeassistant.core import (
    HomeAssistant,
    callback,
)
from homeassistant.config_entries import ConfigEntry

import re

# from homeassistant.exceptions import ConfigEntryAuthFailed
# from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

# , UpdateFailed

from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfFrequency,
    UnitOfTemperature,
    PERCENTAGE,
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
    privateAPI = coordinator.redback.isPrivateAPI()
    hasBattery = await coordinator.redback.hasBattery()

    # Private API has different entities
    # Note: private API always creates battery entities, need examples without
    # battery so the hasBattery() method can be updated to suit
    if privateAPI:
        entities = [
            RedbackChargeSensor(
                coordinator,
                {
                    "name": "Battery SoC",
                    "id_suffix": "battery_soc",
                    "data_source": "BatterySoC0to100",
                },
            ),
            RedbackPowerSensor(
                coordinator,
                {
                    "name": "Load Power",
                    "id_suffix": "load_power",
                    "data_source": "ACLoadW",
                    "convertkW": True,
                },
            ),
            RedbackPowerSensor(
                coordinator,
                {
                    "name": "Backup Load Power",
                    "id_suffix": "backup_load_power",
                    "data_source": "BackupLoadW",
                    "convertkW": True,
                },
            ),
            RedbackPowerSensor(
                coordinator,
                {
                    "name": "Solar Power",
                    "id_suffix": "solar_power",
                    "data_source": "PVW",
                    "convertkW": True,
                },
            ),
            RedbackPowerSensor(
                coordinator,
                {
                    "name": "Battery Power",
                    "id_suffix": "battery_power",
                    "data_source": "BatteryNegativeIsChargingW",
                    "convertkW": True,
                },
            ),
            RedbackPowerSensor(
                coordinator,
                {
                    "name": "Grid Power",
                    "id_suffix": "grid_power",
                    "data_source": "GridNegativeIsImportW",
                    "convertkW": True,
                },
            ),
            RedbackEnergySensor(
                coordinator,
                {
                    "name": "Grid Export",
                    "id_suffix": "grid_export",
                    "data_source": "GridNegativeIsImportW",
                    "direction": "positive",
                    "convertkW": True,
                },
            ),
            RedbackEnergySensor(
                coordinator,
                {
                    "name": "Grid Import",
                    "id_suffix": "grid_import",
                    "data_source": "GridNegativeIsImportW",
                    "direction": "negative",
                    "convertkW": True,
                },
            ),
            RedbackEnergySensor(
                coordinator,
                {
                    "name": "Solar Generation",
                    "id_suffix": "solar_gen",
                    "data_source": "PVW",
                    "direction": "positive",
                    "convertkW": True,
                },
            ),
            RedbackEnergySensor(
                coordinator,
                {
                    "name": "Battery Charge",
                    "id_suffix": "battery_charge_total",
                    "data_source": "BatteryNegativeIsChargingW",
                    "direction": "negative",
                    "convertkW": True,
                },
            ),
            RedbackEnergySensor(
                coordinator,
                {
                    "name": "Battery Discharge",
                    "id_suffix": "battery_discharge_total",
                    "data_source": "BatteryNegativeIsChargingW",
                    "direction": "positive",
                    "convertkW": True,
                },
            ),
            RedbackEnergySensor(
                coordinator,
                {
                    "name": "Load Energy",
                    "id_suffix": "load_energy",
                    "data_source": "ACLoadW",
                    "direction": "positive",
                    "convertkW": True,
                },
            ),
            RedbackEnergySensor(
                coordinator,
                {
                    "name": "Backup Load Energy",
                    "id_suffix": "backup_load_energy",
                    "data_source": "BackupLoadW",
                    "direction": "positive",
                    "convertkW": True,
                },
            ),
        ]

    # Public API has different entities
    else:
        entities = [
            RedbackVoltageSensor(
                coordinator,
                {
                    "name": "Grid Voltage A",
                    "id_suffix": "grid_v_a",
                    "data_source": "VoltageInstantaneousV_A",
                },
            ),
            RedbackVoltageSensor(
                coordinator,
                {
                    "name": "Grid Voltage B",
                    "id_suffix": "grid_v_b",
                    "data_source": "VoltageInstantaneousV_B",
                },
            ),
            RedbackVoltageSensor(
                coordinator,
                {
                    "name": "Grid Voltage C",
                    "id_suffix": "grid_v_c",
                    "data_source": "VoltageInstantaneousV_C",
                },
            ),
            RedbackVoltageSensor(
                coordinator,
                {
                    "name": "Grid Voltage",
                    "id_suffix": "grid_v",
                    "data_source": "VoltageInstantaneousV",
                },
            ),
            RedbackTempSensor(
                coordinator,
                {
                    "name": "Inverter Temperature",
                    "id_suffix": "inverter_temp",
                    "data_source": "InverterTemperatureC",
                },
            ),
            RedbackFrequencySensor(
                coordinator,
                {
                    "name": "Grid Frequency",
                    "id_suffix": "grid_freq",
                    "data_source": "FrequencyInstantaneousHz",
                },
            ),
            RedbackEnergyMeter(
                coordinator,
                {
                    "name": "Solar Generation Total",
                    "id_suffix": "pv_total",
                    "data_source": "PvAllTimeEnergykWh",
                },
            ),
            RedbackEnergyMeter(
                coordinator,
                {
                    "name": "Site Load Total",
                    "id_suffix": "load_total",
                    "data_source": "LoadAllTimeEnergykWh",
                },
            ),
            RedbackEnergyMeter(
                coordinator,
                {
                    "name": "Grid Export Total",
                    "id_suffix": "export_total",
                    "data_source": "ExportAllTimeEnergykWh",
                },
            ),
            RedbackEnergyMeter(
                coordinator,
                {
                    "name": "Grid Import Total",
                    "id_suffix": "import_total",
                    "data_source": "ImportAllTimeEnergykWh",
                },
            ),
            RedbackPowerSensor(
                coordinator,
                {
                    "name": "Grid Export",
                    "id_suffix": "grid_export",
                    "data_source": "ActiveExportedPowerInstantaneouskW",
                },
            ),
            RedbackPowerSensor(
                coordinator,
                {
                    "name": "Grid Import",
                    "id_suffix": "grid_import",
                    "data_source": "ActiveImportedPowerInstantaneouskW",
                },
            ),
            RedbackPowerSensor(
                coordinator,
                {
                    "name": "Solar Generation",
                    "id_suffix": "pv_power",
                    "data_source": "PvPowerInstantaneouskW",
                },
            ),
            RedbackPowerSensor(
                coordinator,
                {
                    "name": "Site Load",
                    "id_suffix": "load_power",
                    "data_source": "$calc$ float(ed['PvPowerInstantaneouskW']) + float(ed['BatteryPowerNegativeIsChargingkW'] if ed['BatteryPowerNegativeIsChargingkW'] else 0) - float(ed['ActiveExportedPowerInstantaneouskW']) + float(ed['ActiveImportedPowerInstantaneouskW'])",
                },
            ),
        ]
        if hasBattery:
            entities.extend([
                RedbackChargeSensor(
                    coordinator,
                    {
                        "name": "Battery SoC",
                        "id_suffix": "battery_soc",
                        "data_source": "BatterySoCInstantaneous0to1",
                        "convertPercent": True,
                    },
                ),
                RedbackPowerSensor(
                    coordinator,
                    {
                        "name": "Battery Discharge",
                        "id_suffix": "battery_discharge",
                        "data_source": "BatteryPowerNegativeIsChargingkW",
                        "direction": "positive",
                    },
                ),
                RedbackPowerSensor(
                    coordinator,
                    {
                        "name": "Battery Charge",
                        "id_suffix": "battery_charge",
                        "data_source": "BatteryPowerNegativeIsChargingkW",
                        "direction": "negative",
                    },
                ),
                RedbackEnergySensor(
                    coordinator,
                    {
                        "name": "Battery Discharge Total",
                        "id_suffix": "battery_discharge_total",
                        "data_source": "BatteryPowerNegativeIsChargingkW",
                        "direction": "positive",
                    },
                ),
                RedbackEnergySensor(
                    coordinator,
                    {
                        "name": "Battery Charge Total",
                        "id_suffix": "battery_charge_total",
                        "data_source": "BatteryPowerNegativeIsChargingkW",
                        "direction": "negative",
                    },
                ),
                RedbackEnergyStorageSensor(
                    coordinator,
                    {
                        "name": "Battery Capacity",
                        "id_suffix": "battery_capacity",
                        "data_source": "BatteryCapacitykWh",
                    },
                ),
                RedbackEnergyStorageSensor(
                    coordinator,
                    {
                        "name": "Usable Battery Capacity",
                        "id_suffix": "battery_usable_capacity",
                        "data_source": "UsableBatteryCapacitykWh",
                    },
                ),
            ])

    async_add_entities(entities)


class RedbackChargeSensor(RedbackEntity, SensorEntity):
    """Sensor for battery state-of-charge"""

    _attr_name = "Battery SoC"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.BATTERY

    @property
    def unique_id(self) -> str:
        """Device Uniqueid."""
        return f"{self.base_unique_id}_{self.id_suffix}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        LOGGER.debug("Updating entity: %s", self.unique_id)
        self._attr_native_value = self.coordinator.energy_data[self.data_source]
        if self.convertPercent: self._attr_native_value *= 100
        self.async_write_ha_state()

class RedbackTempSensor(RedbackEntity, SensorEntity):
    """Sensor for temperature"""

    _attr_name = "Temperature"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE

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

class RedbackFrequencySensor(RedbackEntity, SensorEntity):
    """Sensor for frequency"""

    _attr_name = "Frequency"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfFrequency.HERTZ
    _attr_device_class = SensorDeviceClass.FREQUENCY

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

class RedbackVoltageSensor(RedbackEntity, SensorEntity):
    """Sensor for voltage"""

    _attr_name = "Voltage"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_device_class = SensorDeviceClass.VOLTAGE

    @property
    def unique_id(self) -> str:
        """Device Uniqueid."""
        return f"{self.base_unique_id}_{self.id_suffix}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        LOGGER.debug("Updating entity: %s", self.unique_id)
        self._attr_native_value = self.coordinator.energy_data.get(self.data_source, 0)
        self.async_write_ha_state()

class RedbackPowerSensor(RedbackEntity, SensorEntity):
    """Sensor for power"""

    _attr_name = "Power"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
    _attr_device_class = SensorDeviceClass.POWER

    @property
    def unique_id(self) -> str:
        """Device Uniqueid."""
        return f"{self.base_unique_id}_{self.id_suffix}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        LOGGER.debug("Updating entity: %s", self.unique_id)

        measurement = 0
        # dynamically calculated power measurement
        if self.data_source.startswith('$calc$'):
            measurement = re.sub('^\$calc\$\s*', '', self.data_source)
            ed = self.coordinator.energy_data
            measurement = float(eval(measurement, {'ed':ed}))

        # direct power measurement
        else:
            measurement = self.coordinator.energy_data[self.data_source]

        if (self.direction == "positive"):
            measurement = max(measurement, 0)
        elif (self.direction == "negative"):
            measurement = 0 - min(measurement, 0)
        self._attr_native_value = measurement
        if self.convertkW: self._attr_native_value /= 1000 # convert from W to kW
        self.async_write_ha_state()

class RedbackEnergySensor(RedbackEntity, SensorEntity):
    """Sensor for energy"""

    _attr_name = "Energy"
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY

    def __init__(self, coordinator: RedbackDataUpdateCoordinator, details) -> None:        
        super().__init__(coordinator, details)
        self._attr_native_value = 0
        self._attr_last_reset = datetime.now()
        self._last_update = datetime.now()
        

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
            measurement = 0 - min(measurement, 0)
        sample_time = datetime.now()
        time_delta = sample_time - self._last_update    # Assume sample value is representative of the time since last update
        self._last_update = sample_time
        hours = time_delta.total_seconds()/3600
        self._attr_native_value = measurement * hours  # multiply watts by hours to get Wh
        if self.convertkW: self._attr_native_value /= 1000 # convert from Wh to kWh
        self.async_write_ha_state()

class RedbackEnergyMeter(RedbackEntity, SensorEntity):
    """Sensor for energy metering"""

    _attr_name = "Energy Meter"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY

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

class RedbackEnergyStorageSensor(RedbackEntity, SensorEntity):
    """Sensor for energy storage"""

    _attr_name = "Energy Storage"
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    # this class not availabe until 2023.4 # _attr_device_class = SensorDeviceClass.ENERGY_STORAGE 
    _attr_device_class = SensorDeviceClass.ENERGY

    @property
    def unique_id(self) -> str:
        """Device Uniqueid."""
        return f"{self.base_unique_id}_{self.id_suffix}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        LOGGER.debug("Updating entity: %s", self.unique_id)
        # note: this sensor type always draws from inverter_info, not energy_data
        self._attr_native_value = self.coordinator.inverter_info[self.data_source]
        self.async_write_ha_state()

