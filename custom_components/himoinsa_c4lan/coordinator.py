"""Data update coordinator for the Himoinsa C4LAN integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    COIL_COUNT,
    COIL_START,
    CONNECT_TIMEOUT,
    DOMAIN,
    ENGINE_HOURS_ADDR,
    INPUT_REG_COUNT,
    INPUT_REG_START,
)

_LOGGER = logging.getLogger(__name__)


async def async_read(method, address: int, count: int, slave: int):
    """Call a pymodbus read method, tolerating the slave/device_id rename.

    pymodbus renamed the ``slave`` keyword to ``device_id`` in newer releases;
    Home Assistant may ship either. Try ``slave`` first, fall back to
    ``device_id`` if that signature is rejected.
    """
    try:
        return await method(address, count=count, slave=slave)
    except TypeError:
        return await method(address, count=count, device_id=slave)


class HimoinsaCoordinator(DataUpdateCoordinator[dict]):
    """Polls the C4LAN device and exposes registers + coils to entities."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        slave: int,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self._slave = slave
        self._host = host
        self._port = port
        self._client = AsyncModbusTcpClient(host, port=port, timeout=CONNECT_TIMEOUT)

    async def _async_update_data(self) -> dict:
        if not self._client.connected:
            await self._client.connect()
        if not self._client.connected:
            raise UpdateFailed(f"Cannot connect to {self._host}:{self._port}")

        try:
            # Live telemetry block (addresses 7..31). Addresses 0..6 are
            # grid-only and would fail the whole read, so we start at 7.
            regs = await async_read(
                self._client.read_input_registers,
                INPUT_REG_START, INPUT_REG_COUNT, self._slave,
            )
            if regs.isError():
                raise UpdateFailed(f"Input register read error: {regs}")

            coils = await async_read(
                self._client.read_coils, COIL_START, COIL_COUNT, self._slave
            )
            if coils.isError():
                raise UpdateFailed(f"Coil read error: {coils}")

            registers = {
                INPUT_REG_START + i: value for i, value in enumerate(regs.registers)
            }

            # Engine hours sits outside the main block; best-effort.
            hours = await async_read(
                self._client.read_input_registers, ENGINE_HOURS_ADDR, 1, self._slave
            )
            if not hours.isError():
                registers[ENGINE_HOURS_ADDR] = hours.registers[0]

            return {
                "registers": registers,
                "coils": {i: bool(b) for i, b in enumerate(coils.bits[:COIL_COUNT])},
            }
        except ModbusException as err:
            raise UpdateFailed(f"Modbus error: {err}") from err

    async def async_shutdown(self) -> None:
        """Close the Modbus connection."""
        await super().async_shutdown()
        self._client.close()
