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
                RedbackChargeSensorRaw(
                    coordinator,
                    {
                        "name": "Battery SoC Raw",
                        "id_suffix": "battery_soc_raw",
                        "data_source": "BatterySoCInstantaneous0to1",
                    },
                ),
                RedbackPowerSensor(
                    coordinator,
                    {
                        "name": "Battery Power Flow",
                        "id_suffix": "battery_power",
                        "data_source": "BatteryPowerNegativeIsChargingkW",
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
                RedbackBatteryChargeSensor(
                    coordinator,
                    {
                        "name": "Battery Current Storage",
                        "id_suffix": "battery_current_storage",
                        "data_source": "",
                    },
                ),
            ])

    async_add_entities(entities)

class RedbackChargeSensor(RedbackEntity, SensorEntity):
    """Sensor for battery state-of-charge"""

    _attr_name = None
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.ENERGY
    
    @property
    def unique_id(self) -> str:
        """Device Uniqueid."""
        return f"{self.base_unique_id}_{self.id_suffix}"
    
    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return additional pieces of information."""
        dataAttributes = self.coordinator.inverter_info

        if dataAttributes is None:
            data["min_offgrid_soc_0to1"] = None
            data["min_ongrid_soc_0to1"] = None
        else:
            data = {
                "min_offgrid_soc_0to1": (dataAttributes["MinOffgridSoC0to1"] ),
                "min_ongrid_soc_0to1": (dataAttributes["MinSoC0to1"] )
            }
        return data
    
    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        LOGGER.debug("Updating entity: %s", self.unique_id)
        self._attr_native_value = self.coordinator.energy_data[self.data_source]
        if self.convertPercent: self._attr_native_value *= 100
        self.async_write_ha_state()

class RedbackChargeSensorRaw(RedbackEntity, SensorEntity):
    """Sensor for battery state-of-charge"""

    _attr_name = None
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
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
        if self.data_source.startswith("$calc$"):
            measurement = re.sub("^\$calc\$\s*", "", self.data_source)
            ed = self.coordinator.energy_data
            measurement = float(eval(measurement, {"ed":ed}))

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
        self._attr_native_value = (measurement / 60) # we"re measuring in hours, but reporting in minutes, so divide out accordingly
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
    
    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return additional pieces of information."""
        dataAttributes = self.coordinator.inverter_info

        if dataAttributes is None:
            data["usable_battery_offgrid_kwh"] = None
            data["usable_battery_ongrid_kwh"] = None
            data["max_discharge_power_w"] = None
            data["max_charge_power_w"] = None
        else: 
            data = {
				"usable_battery_offgrid_kwh": dataAttributes["UsableBatteryCapacitykWh"],
				"usable_battery_ongrid_kwh": dataAttributes["UsableBatteryCapacityOnGridkWh"],
				"max_discharge_power_w": dataAttributes["BatteryMaxDischargePowerW"],
				"max_charge_power_w": dataAttributes["BatteryMaxChargePowerW"]
			}
        return data

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
        self._attr_native_value = round(self.coordinator.energy_data[self.data_source],0)
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

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return additional pieces of information."""
        dataAttributes = self.coordinator.inverter_info

        if dataAttributes is None:
            data["serial_number"] = None
            data["software_version"] = None
            data["ross_version"] = None
            data["model_name"] = None
            data["system_type"] = None
            data["site_id"] = None
            data ["inverter_max_export_power_w"] = None
            data ["inverter_max_import_power_w"] = None
            
        else: 
            data = {
				"serial_number": dataAttributes["SerialNumber"],
				"software_version": dataAttributes["SoftwareVersion"],
				"ross_version": dataAttributes["SoftwareVersion"],
                "model_name": dataAttributes["ModelName"],
                "system_type": dataAttributes["SystemType"],
                "site_id": dataAttributes["SiteId"],
                "inverter_max_export_power_w": dataAttributes["InverterMaxExportPowerW"],
                "inverter_max_import_power_w": dataAttributes["InverterMaxImportPowerW"]
			}
        return data

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

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return additional pieces of information."""
        dataAttributes = self.coordinator.energy_data

        if dataAttributes is None:
            data["inverter_power_setting"] = None
        else: 
            data = {
				"inverter_power_setting": dataAttributes["InverterPowerW"]
			}
        return data


    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        LOGGER.debug("Updating entity: %s", self.unique_id)
        self._attr_native_value = self.coordinator.energy_data[self.data_source]
        self.async_write_ha_state()
        
class RedbackBatteryChargeSensor(RedbackEntity, SensorEntity):
    """Sensor for inverter mode"""

    _attr_name = "Energy Storage"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY_STORAGE 
    _attr_icon = "mdi:home-battery"

    @property
    def unique_id(self) -> str:
        """Device Uniqueid."""
        return f"{self.base_unique_id}_{self.id_suffix}"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return additional pieces of information."""
        dataAttributesEnergy = self.coordinator.energy_data
        dataAttributesInfo = self.coordinator.inverter_info

        data = {
		    "battery_current_ongrid_usable": round( ((dataAttributesEnergy["BatterySoCInstantaneous0to1"]  - dataAttributesInfo["MinSoC0to1"]) * dataAttributesInfo["BatteryCapacitykWh"]), 3),
            "battery_current_offgrid_usable": round( ((dataAttributesEnergy["BatterySoCInstantaneous0to1"] - dataAttributesInfo["MinOffgridSoC0to1"]) * dataAttributesInfo["BatteryCapacitykWh"]), 3),
			}
        return data

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        LOGGER.debug("Updating entity: %s", self.unique_id)
        batterySoc= self.coordinator.energy_data["BatterySoCInstantaneous0to1"]
        batteryCapacity= self.coordinator.inverter_info["BatteryCapacitykWh"]
        self._attr_native_value = round( (batterySoc * batteryCapacity), 3)
        self.async_write_ha_state()
        

        
