"""Constants for the Himoinsa C4LAN integration."""
from __future__ import annotations

DOMAIN = "himoinsa_c4lan"

# Config keys
CONF_SLAVE = "slave"
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_NAME = "Himoinsa Generator"
DEFAULT_PORT = 502
DEFAULT_SLAVE = 1
DEFAULT_SCAN_INTERVAL = 30  # seconds
CONNECT_TIMEOUT = 5

# --- Himoinsa C4LAN Modbus map (verified against the official app) ---
# Live telemetry is in INPUT REGISTERS (function 04). Addresses 0..6 are
# grid measurements ("Only central CEA7") and raise exception 4 on a standard
# genset, so the block read MUST start at address 7.
INPUT_REG_START = 7
INPUT_REG_COUNT = 25  # addresses 7..31
ENGINE_HOURS_ADDR = 42  # total engine hours (hh); reg 41 is the mm:ss part
COIL_START = 0
COIL_COUNT = 10  # generator status/command coils 0..9

# Raw values that mean "sensor not present / read error" (manual: FFh / FEh).
NOT_AVAILABLE = (0xFFFF, 0xFFFE)
