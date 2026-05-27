"""Binary sensor platform for the Himoinsa C4LAN integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import HimoinsaCoordinator
from .entity import HimoinsaEntity


@dataclass(frozen=True, kw_only=True)
class HimoinsaBinaryEntityDescription(BinarySensorEntityDescription):
    """Binary sensor description carrying the coil index."""

    coil: int


# Coil map (function 01): 0 Reset, 1 Started, 2 Stopped, 3 Auto, 4 Manual,
# 5 Test, 6 Lock, 7 Transfer pump, 8 Group contactor, 9 Grid contactor.
BINARY_SENSORS: tuple[HimoinsaBinaryEntityDescription, ...] = (
    HimoinsaBinaryEntityDescription(
        key="generator_running", name="Generator running", coil=1,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    HimoinsaBinaryEntityDescription(
        key="generator_stopped", name="Generator stopped", coil=2,
        icon="mdi:engine-off",
    ),
    HimoinsaBinaryEntityDescription(
        key="auto_mode", name="Auto mode", coil=3, icon="mdi:cog-autorenew",
    ),
    HimoinsaBinaryEntityDescription(
        key="manual_mode", name="Manual mode", coil=4, icon="mdi:hand-back-right",
    ),
    HimoinsaBinaryEntityDescription(
        key="test_mode", name="Test mode", coil=5, icon="mdi:test-tube",
    ),
    HimoinsaBinaryEntityDescription(
        key="lock_mode", name="Lock mode", coil=6, icon="mdi:lock",
    ),
    HimoinsaBinaryEntityDescription(
        key="transfer_pump", name="Transfer pump", coil=7,
        device_class=BinarySensorDeviceClass.RUNNING, icon="mdi:pump",
    ),
    HimoinsaBinaryEntityDescription(
        key="group_contactor", name="Group contactor", coil=8,
        device_class=BinarySensorDeviceClass.POWER,
    ),
    HimoinsaBinaryEntityDescription(
        key="grid_contactor", name="Grid contactor", coil=9,
        device_class=BinarySensorDeviceClass.POWER,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Himoinsa binary sensors from a config entry."""
    coordinator: HimoinsaCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[BinarySensorEntity] = [
        HimoinsaBinarySensor(coordinator, entry.entry_id, description)
        for description in BINARY_SENSORS
    ]
    entities.append(HimoinsaConnectionSensor(coordinator, entry.entry_id))
    async_add_entities(entities)


class HimoinsaBinarySensor(HimoinsaEntity, BinarySensorEntity):
    """A single coil-backed binary sensor."""

    entity_description: HimoinsaBinaryEntityDescription

    def __init__(
        self,
        coordinator: HimoinsaCoordinator,
        entry_id: str,
        description: HimoinsaBinaryEntityDescription,
    ) -> None:
        super().__init__(coordinator, entry_id, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data["coils"].get(self.entity_description.coil)


class HimoinsaConnectionSensor(HimoinsaEntity, BinarySensorEntity):
    """Connectivity sensor: on = device reachable, off = polling failed.

    Unlike the other entities, this stays *available* when the device drops,
    so it reports 'off' instead of becoming unavailable — which makes it
    usable as a reliable trigger for a 'connection lost' notification.
    """

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_name = "Connection"

    def __init__(self, coordinator: HimoinsaCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id, "connection")

    @property
    def available(self) -> bool:
        return True

    @property
    def is_on(self) -> bool:
        return self.coordinator.last_update_success
