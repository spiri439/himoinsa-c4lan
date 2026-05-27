# Himoinsa C4LAN Generator — Home Assistant integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Monitor a Himoinsa generator fitted with a **C4LAN MODBUS** communications
device (CE7-family controllers: CEM7 / CEA7 / C4) directly in Home Assistant
over Modbus TCP. Local polling — no cloud.

## Features

Creates one device with:

**Sensors** — group frequency, line/phase voltages (L1-L2, L2-L3, L3-L1,
L1-N, L2-N, L3-N), phase currents, active/apparent/reactive power, engine
speed, fuel level, charge-alternator voltage, battery voltage, coolant
temperature, oil pressure, auxiliary temperature, engine hours.

**Binary sensors** — generator running, generator stopped, auto mode, manual
mode, test mode, lock mode, transfer pump, group contactor, grid contactor.

Sensors that the controller reports as "not connected" (`0xFFFF`) appear as
*unknown* rather than a bogus value.

## Installation (HACS)

1. HACS → ⋮ → **Custom repositories**.
2. Add `https://github.com/spiri439/himoinsa-c4lan` with category **Integration**.
3. Install **Himoinsa C4LAN Generator**, then restart Home Assistant.
4. **Settings → Devices & Services → Add Integration → Himoinsa C4LAN**.

### Manual installation

Copy `custom_components/himoinsa_c4lan` into your Home Assistant
`config/custom_components/` directory and restart.

## Configuration

| Field | Default | Notes |
|-------|---------|-------|
| Host / IP | — | IP of the C4LAN MODBUS device |
| Port | 502 | Modbus TCP port |
| Slave/unit ID | 1 | "Slave Offset" (1) + generator index; generator 0 = 1 |
| Scan interval | 30 s | Adjustable later via the integration options |

## How it reads the device

Live telemetry lives in **input registers (function 04)**. Addresses 0–6 are
grid measurements ("Only central CEA7") and raise exception 4 on a standard
genset, so the integration reads the block starting at **address 7**. Values
are scaled per the C4LAN manual: fuel is per-mille (÷10 → %), battery and
charge-alternator are deci-volts (÷10 → V), coolant/aux are deci-°C (÷10),
oil is deci-bar, frequency is deci-Hz. Generator status comes from
**coils 0–9** (function 01). Engine hours is input register 42.

## Disclaimer

Not affiliated with or endorsed by HIMOINSA s.l. "Himoinsa" and "C4LAN" are
trademarks of their respective owner. Use at your own risk.
