"""Base entity for the Himoinsa C4LAN integration."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HimoinsaCoordinator


class HimoinsaEntity(CoordinatorEntity[HimoinsaCoordinator]):
    """Shared device info / coordinator wiring for all entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: HimoinsaCoordinator, entry_id: str, key: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="C4LAN Generator",
            manufacturer="spiri439",
            model="C4LAN for Himoinsa",
        )
