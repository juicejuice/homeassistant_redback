"""Redback sensors for the Redback integration."""
from __future__ import annotations
from collections.abc import Mapping

from datetime import (datetime, timedelta)
from typing import Any
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
    UnitOfElectricCurrent,
    PERCENTAGE,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)
from .const import DOMAIN, LOGGER, INVERTER_MODES, INVERTER_STATUS
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
            RedbackCurrentSensor(
                coordinator,
                {
                    "name": "Grid Current A",
                    "id_suffix": "grid_a_a",
                    "data_source": "CurrentInstantaneousA_A",
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
            RedbackCurrentSensor(
                coordinator,
                {
                    "name": "Grid Current B",
                    "id_suffix": "grid_a_b",
                    "data_source": "CurrentInstantaneousA_B",
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
            RedbackCurrentSensor(
                coordinator,
                {
                    "name": "Grid Current C",
                    "id_suffix": "grid_a_c",
                    "data_source": "CurrentInstantaneousA_C",
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
            RedbackCurrentSensor(
                coordinator,
                {
                    "name": "Grid Current Net",
                    "id_suffix": "grid_a_net",
                    "data_source": "CurrentInstantaneousA",
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
                    "name": "Grid Net",
                    "id_suffix": "grid_net",
                    "data_source": "ActiveNetPowerInstantaneouskW",
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
                    "data_source": "$calc$ float(ed['PvPowerInstantaneouskW']) + float(ed['BatteryPowerNegativeIsChargingkW']) - float(ed['ActiveExportedPowerInstantaneouskW']) + float(ed['ActiveImportedPowerInstantaneouskW'])",
                },
            ),
            RedbackStatusSensor(
                coordinator,
                {
                    "name": "Inverter Status",
                    "id_suffix": "inverter_status",
                    "data_source": "Status",
                }
            ),
            RedbackPowerSensorStatic(
                coordinator,
                {
                    "name": "Inverter Max Export Power",
                    "id_suffix": "inverter_max_export_power",
                    "data_source": "InverterMaxExportPowerW",
                },
            ),
            RedbackPowerSensorStatic(
                coordinator,
                {
                    "name": "Inverter Max Import Power",
                    "id_suffix": "inverter_max_import_power",
                    "data_source": "InverterMaxImportPowerW",
                },
            ),
            
            RedbackPowerSensorW(
                coordinator,
                {
                    "name": "Inverter Power Setpoint",
                    "id_suffix": "inverter_powerw",
                    "data_source": "InverterPowerW",
                },
            ),
            RedbackInverterModeSensor(
                coordinator,
                {
                    "name": "Inverter Mode",
                    "id_suffix": "inverter_mode",
                    "data_source": "InverterMode",
                },
            ),
            RedBackSoftwareVersionSensor(
                coordinator,
                {
                    "name": "Software Version",
                    "id_suffix": "software_version",
                    "data_source": "SoftwareVersion",
                }
            ),
            RedBackSoftwareVersionSensor(
                coordinator,
                {
                    "name": "Serial Number",
                    "id_suffix": "serial_number",
                    "data_source": "SerialNumber",
                }
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
                        "data_source_2": "MinSoC0to1",
                        "convertPercent": True,
                    },
                ),
                RedbackChargeSensorInfo(
                    coordinator,
                    {
                        "name": "Battery Min On Grid SoC",
                        "id_suffix": "battery_min_ongrid_soc0to1",
                        "data_source": "MinSoC0to1",
                        "convertPercent": True,
                    },
                ),
                RedbackChargeSensorInfo(
                    coordinator,
                    {
                        "name": "Battery Min off Grid SoC",
                        "id_suffix": "battery_min_offgrid_soc0to1",
                        "data_source": "MinOffgridSoC0to1",
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
                RedbackPowerSensorStatic(
                    coordinator,
                    {
                        "name": "Battery Max Charge Power",
                        "id_suffix": "battery_max_charge_power",
                        "data_source": "BatteryMaxChargePowerW",
                    },
                ),
                RedbackPowerSensorStatic(
                    coordinator,
                    {
                        "name": "Battery Max Discharge Power",
                        "id_suffix": "battery_max_discharge_power",
                        "data_source": "BatteryMaxDischargePowerW",
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
                        "name": "Battery Capacity Usable Off Grid",
                        "id_suffix": "battery_capacity_usable_off_grid",
                        "data_source": "UsableBatteryCapacitykWh",
                    },
                ),
                RedbackEnergyStorageSensor(
                    coordinator,
                    {
                        "name": "Battery Capacity Usable On Grid",
                        "id_suffix": "battery_capacity_usable_on_grid",
                        "data_source": "UsableBatteryCapacityOnGridkWh",
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

class RedbackChargeSensorInfo(RedbackEntity, SensorEntity):
    """Sensor for battery state-of-charge"""

    _attr_name = "SoC"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_min_ongrid_soc = "MinSoC0to1"

    @property
    def unique_id(self) -> str:
        """Device Uniqueid."""
        return f"{self.base_unique_id}_{self.id_suffix}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        LOGGER.debug("Updating entity: %s", self.unique_id)
        self._attr_native_value = self.coordinator.inverter_info[self.data_source]
        self._attr_min_ongrid_soc = self.coordinator.inverter_info["MinSoC0to1"]
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
        
class RedbackPowerSensorStatic(RedbackEntity, SensorEntity):
    _attr_name = "Power"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER

    @property
    def unique_id(self) -> str:
        """Device Uniqueid."""
        return f"{self.base_unique_id}_{self.id_suffix}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        LOGGER.debug("Updating entity: %s", self.unique_id)
        self._attr_native_value = self.coordinator.inverter_info[self.data_source]
        self.async_write_ha_state()

class RedbackPowerSensorW(RedbackEntity, SensorEntity):
    _attr_name = "Power"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER

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

class RedbackEnergySensor(RedbackEntity, SensorEntity):
    """Sensor for energy"""

    _attr_name = "Energy"
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _suggested_display_precision = 3

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
        self._attr_last_reset = datetime.now() - timedelta(minutes=1)
        self._attr_native_value = measurement / 60 # we're measuring in hours, but reporting in minutes, so divide out accordingly
        if self.convertkW: self._attr_native_value /= 1000 # convert from W to kW
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
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY_STORAGE 
    _attr_icon = "mdi:home-battery"

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

class RedbackCurrentSensor(RedbackEntity, SensorEntity):
    """Sensor for Current"""

    _attr_name = "Current"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_device_class = SensorDeviceClass.CURRENT
    _suggested_display_precision = 3

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

class RedbackStatusSensor(RedbackEntity, SensorEntity):
    """Sensor for state"""

    _attr_name = "State"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = INVERTER_STATUS
    _attr_native_unit_of_measurement = None
    _attr_icon = "mdi:information-outline"

    @property
    def unique_id(self) -> str:
        """Device Uniqueid."""
        return f"{self.base_unique_id}_{self.id_suffix}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        LOGGER.debug("Updating entity: %s", self.unique_id)
        self._attr_native_value = self.coordinator.inverter_info[self.data_source]
        self.async_write_ha_state()
        
class RedbackInverterModeSensor(RedbackEntity, SensorEntity):
    """Sensor for inverter mode"""

    _attr_name = "state"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = INVERTER_MODES
    _attr_native_unit_of_measurement = None
    _attr_icon = "mdi:information-outline"

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
        
class RedBackSoftwareVersionSensor(RedbackEntity, SensorEntity ):
    """Sensor for software version"""

    _attr_name = "string"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_native_unit_of_measurement = None
    _attr_icon = "mdi:information-outline"

    @property
    def unique_id(self) -> str:
        """Device Uniqueid."""
        return f"{self.base_unique_id}_{self.id_suffix}"
        
    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        LOGGER.debug("Updating entity: %s", self.unique_id)        
        self._attr_native_value = self.coordinator.inverter_info[self.data_source]
        self.async_write_ha_state()


        
