"""Config flow for the Himoinsa C4LAN integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_SLAVE,
    CONNECT_TIMEOUT,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE,
    DOMAIN,
    INPUT_REG_START,
)
from .coordinator import async_read

_LOGGER = logging.getLogger(__name__)


async def _test_connection(host: str, port: int, slave: int) -> str | None:
    """Return None on success or an error key on failure."""
    client = AsyncModbusTcpClient(host, port=port, timeout=CONNECT_TIMEOUT)
    try:
        if not await client.connect():
            return "cannot_connect"
        result = await async_read(client.read_input_registers, INPUT_REG_START, 1, slave)
        if result.isError():
            return "invalid_response"
    except (ModbusException, asyncio.TimeoutError, OSError) as err:
        _LOGGER.warning("C4LAN connection test failed: %s", err)
        return "cannot_connect"
    except Exception:  # noqa: BLE001 - surface as a clean error instead of "unknown"
        _LOGGER.exception("Unexpected error testing C4LAN connection")
        return "unknown"
    finally:
        client.close()
    return None


class HimoinsaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the UI configuration flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}:{user_input[CONF_SLAVE]}"
            )
            self._abort_if_unique_id_configured()
            error = await _test_connection(
                user_input[CONF_HOST], user_input[CONF_PORT], user_input[CONF_SLAVE]
            )
            if error:
                errors["base"] = error
            else:
                return self.async_create_entry(title=DEFAULT_NAME, data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Required(CONF_SLAVE, default=DEFAULT_SLAVE): int,
                vol.Required(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): vol.All(int, vol.Range(min=5, max=3600)),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return HimoinsaOptionsFlow()


class HimoinsaOptionsFlow(OptionsFlow):
    """Allow changing the scan interval after setup."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        schema = vol.Schema(
            {
                vol.Required(CONF_SCAN_INTERVAL, default=current): vol.All(
                    int, vol.Range(min=5, max=3600)
                )
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
