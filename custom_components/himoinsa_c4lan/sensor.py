"""Sensor platform for the Himoinsa C4LAN integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, NOT_AVAILABLE
from .coordinator import HimoinsaCoordinator
from .entity import HimoinsaEntity


@dataclass(frozen=True, kw_only=True)
class HimoinsaSensorEntityDescription(SensorEntityDescription):
    """Sensor description carrying the input-register address and scale divisor."""

    register: int
    scale: float = 1.0


SENSORS: tuple[HimoinsaSensorEntityDescription, ...] = (
    HimoinsaSensorEntityDescription(
        key="group_frequency", name="Group frequency", register=7, scale=10,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY, state_class=SensorStateClass.MEASUREMENT,
    ),
    HimoinsaSensorEntityDescription(
        key="voltage_l12", name="Voltage L1-L2", register=8,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT,
    ),
    HimoinsaSensorEntityDescription(
        key="voltage_l23", name="Voltage L2-L3", register=9,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT,
    ),
    HimoinsaSensorEntityDescription(
        key="voltage_l31", name="Voltage L3-L1", register=10,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT,
    ),
    HimoinsaSensorEntityDescription(
        key="voltage_l1n", name="Voltage L1-N", register=11,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT,
    ),
    HimoinsaSensorEntityDescription(
        key="voltage_l2n", name="Voltage L2-N", register=12,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT,
    ),
    HimoinsaSensorEntityDescription(
        key="voltage_l3n", name="Voltage L3-N", register=13,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT,
    ),
    HimoinsaSensorEntityDescription(
        key="current_l1", name="Current L1", register=14,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT,
    ),
    HimoinsaSensorEntityDescription(
        key="current_l2", name="Current L2", register=15,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT,
    ),
    HimoinsaSensorEntityDescription(
        key="current_l3", name="Current L3", register=16,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT,
    ),
    HimoinsaSensorEntityDescription(
        key="active_power", name="Active power", register=22,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT,
    ),
    HimoinsaSensorEntityDescription(
        key="apparent_power", name="Apparent power", register=23,
        native_unit_of_measurement="kVA", state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
    ),
    HimoinsaSensorEntityDescription(
        key="reactive_power", name="Reactive power", register=24,
        native_unit_of_measurement="kvar", state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
    ),
    HimoinsaSensorEntityDescription(
        key="engine_speed", name="Engine speed", register=25,
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT, icon="mdi:engine",
    ),
    HimoinsaSensorEntityDescription(
        key="fuel_level", name="Fuel level", register=26, scale=10,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT, icon="mdi:fuel",
    ),
    HimoinsaSensorEntityDescription(
        key="charge_alternator_voltage", name="Charge alternator voltage", register=27, scale=10,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT,
    ),
    HimoinsaSensorEntityDescription(
        key="battery_voltage", name="Battery voltage", register=28, scale=10,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT,
    ),
    HimoinsaSensorEntityDescription(
        key="coolant_temperature", name="Coolant temperature", register=29, scale=10,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT,
    ),
    HimoinsaSensorEntityDescription(
        key="oil_pressure", name="Oil pressure", register=30, scale=10,
        native_unit_of_measurement=UnitOfPressure.BAR,
        device_class=SensorDeviceClass.PRESSURE, state_class=SensorStateClass.MEASUREMENT,
    ),
    HimoinsaSensorEntityDescription(
        key="auxiliary_temperature", name="Auxiliary temperature", register=31, scale=10,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT,
    ),
    HimoinsaSensorEntityDescription(
        key="engine_hours", name="Engine hours", register=42,
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION, state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:timer-outline",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Himoinsa sensors from a config entry."""
    coordinator: HimoinsaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        HimoinsaSensor(coordinator, entry.entry_id, description) for description in SENSORS
    )


class HimoinsaSensor(HimoinsaEntity, SensorEntity):
    """A single scaled input-register sensor."""

    entity_description: HimoinsaSensorEntityDescription

    def __init__(
        self,
        coordinator: HimoinsaCoordinator,
        entry_id: str,
        description: HimoinsaSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, entry_id, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | int | None:
        raw = self.coordinator.data["registers"].get(self.entity_description.register)
        if raw is None or raw in NOT_AVAILABLE:
            return None
        if self.entity_description.scale != 1:
            return round(raw / self.entity_description.scale, 1)
        return raw
