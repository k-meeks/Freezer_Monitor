# Freezer Monitor

## What this project is
A battery-powered temperature monitor that lives inside a chest freezer. An nRF52840 reads a DS18B20 temperature sensor and broadcasts the reading over BLE using the BTHome v2 format. **CONFIRMED 2026-06-19: deployed and running live** — board is inside the freezer, waking every 5 minutes, and a BT proxy ([k-meeks/linux_bt_proxy](https://github.com/k-meeks/linux_bt_proxy), a fork the user bug-fixed and runs on a Linux host) reliably relays BTHome events to Home Assistant, with battery and temperature tracked continuously. Theengs Gateway on a nearby NAS remains a documented fallback for range issues. Power comes from a Saft LS14250 Li-SOCl2 cell (3.6V, primary/non-rechargeable) that is manually replaced when depleted — battery life is the dominant design constraint throughout. Carrier PCB ordered 2026-06-18; awaiting boards for assembly and testing (current deployment is on the bench-wired prototype). Firmware complete. Current work: external alerting system (GCP + voip.ms).

Personal project. No git actions requested from Claude (user manages git). No daily-log time tracking for this project.

Sibling project: [AcuRite_Bridge](../AcuRite_Bridge/) (ESP32-C3 + RX470C, decoding AcuRite 00515M sensor broadcasts) — same multi-site family-monitoring intent, deliberately a separate repo since there's no shared code/toolchain between an nRF52840/BLE board and an ESP32-C3/433MHz one. A third repo is planned for the shared GCP/voip.ms alerting backend once both bridges have something to feed it.

## Usage
Firmware confirmed working end-to-end. Build setup:

1. Arduino IDE > Preferences > Additional Boards Manager URLs, add:
   - `https://adafruit.github.io/arduino-board-index/package_adafruit_index.json`
   - `https://github.com/jpconstantineau/Community_nRF52_Arduino/releases/latest/download/package_jpconstantineau_boards_index.json`
2. Boards Manager: install "Adafruit nRF52", then "Community Add on Adafruit nrf52 boards".
3. Select board: **Nice Keyboard's nice!nano** (`nice_nano`, from Community package) — CONFIRMED correct for this clone.
4. Install libraries: `OneWire`, `DallasTemperature` (Bluefruit BLE comes with the Adafruit nRF52 core).
5. Open `firmware/freezer_monitor/freezer_monitor.ino`, build, flash via UF2 bootloader (double-tap RST).
6. Firmware is complete and deployed — `SLEEP_INTERVAL_MS` is `(5UL * 60UL * 1000UL)` (5 min), Serial1 debug scaffolding removed.

HA setup: Settings → Devices & Services → Add Integration → BTHome. Device appears as `FreezerMonitor`.

## Home Assistant / BTHome / Theengs / nRF52 — confirmed quirks
- **Battery is a Saft LS14250 (Li-SOCl2, primary/non-rechargeable, 3.6V nominal, 1/2AA).** Wire to the board's labeled `B+`/`B-` pins (CONFIRMED from board photos 2026-06-15 — see `docs/hardware/teyleten-nrf52840-promicro.md`). This is the only battery input on the board, and it's the charge IC's input — **never plug in USB while the LS14250 is connected to B+/B-** (charging only engages with USB present). Wire through a connector so the cell can be unplugged before reprogramming. "Recharge" = swap the cell. Li-SOCl2 has a very flat discharge curve until near end-of-life, then drops sharply — voltage-based battery % will read near-100% for most of the cell's life. See [[project-failure-alerting]].
- Home Assistant REST API reference saved locally at `docs/home-assistant/rest-api.md` (fetched 2026-06-14).
- BTHome v2 format reference saved locally at `docs/bthome/format-v2.md` (fetched 2026-06-15), including a project-specific summary of which object IDs we'll use (packet id `0x00`, battery `0x01`, temperature `0x02`) and the required ascending object-ID ordering.
- Board hardware notes (Teyleten Pro Micro nRF52840 / nice!nano v2 clone) saved at `docs/hardware/teyleten-nrf52840-promicro.md` (fetched 2026-06-15) — pin numbering convention, Arduino setup, bootloader. Most board-specific details are marked **UNVERIFIED** pending hardware-in-hand testing; promote to this section once confirmed.
- **P0.14 and P0.16 hang/crash-loop the board** as soon as either is configured as GPIO (pinMode/digitalWrite) — CONFIRMED 2026-06-15. Don't use either pin.
- **P0.13 is not broken out on this board's header** — CONFIRMED 2026-06-15. `digitalWrite(13,...)` has no observable effect anywhere (VCC, header pins). Sensor power-gating was dropped; DS18B20 wires directly to `B+`/`B-` instead.
- **`VCC` header pin reads ~0V when running off `B+` alone** — CONFIRMED 2026-06-15. Likely fed from a USB/RAW-derived regulator, not from the battery. Not usable as a peripheral rail on battery power.
- New physical pin-reference convention (easier than silkscreen labels): each header row is numbered **1-13, pin 1 = end farthest from the USB-C connector, pin 13 = the `B-`/`B+` pad itself**. Full left/right table in `docs/hardware/teyleten-nrf52840-promicro.md`.
- **`PIN_VBAT`/A7 (P0.31) and A2 (P0.04) are floating/unusable** — CONFIRMED 2026-06-15, raw ADC readings were pure noise uncorrelated with actual battery voltage on this clone (no internal VBAT divider). Battery voltage is instead read via an **external divider**: two ~1MΩ resistors in series from `B+` to `GND`, midpoint wired to `P0.02`/A0 (right side, position 6). Calibrated empirically against a multimeter (B+=3.56V at raw≈8030) — see `BATT_SCALE` in `firmware/freezer_monitor/freezer_monitor.ino`. ~1.8µA continuous draw, negligible.
- **HA native BTHome integration confirmed working** (2026-06-16) — HA on an Intel N95 NUC with onboard BT picks up `FreezerMonitor` advertisements directly, no Theengs Gateway needed as long as HA's BT radio can reach the device.
- **Chest freezer lid attenuates BLE signal significantly** — confirmed 2026-06-16: signal drops from -54 dBm on desk to -82/-88 dBm in basement when device is inside freezer. TX power bumped to max (+8 dBm) to compensate. **CONFIRMED 2026-06-19: a Linux BT proxy is deployed near the freezer and reliably relays BTHome events to HA** — this is the active path, not just a fallback. Proxy is [k-meeks/linux_bt_proxy](https://github.com/k-meeks/linux_bt_proxy), a fork the user heavily bug-fixed, running on a Linux host (not ESP32). Theengs Gateway on nearby NAS remains an untested fallback if the proxy path ever has issues.
- **P1.06 (left pos 1, Arduino pin 38) used as VREF** — driven HIGH in firmware (`pinMode(38, OUTPUT); digitalWrite(38, HIGH)`) to provide a 3.3V logic reference on the serial debug header. Carrier PCB routes P1.06 → J2 pin 2 (VREF). CP2102 draws negligible current from this GPIO.
- (Add Theengs Gateway config quirks here if/when the fallback path is needed.)

## This One Goes to Eleven
When presenting numbered lists of options to the user, the count must never be exactly 10. Fewer than 10 is fine. More than 10 is fine. But if you arrive at exactly 10 options, you must add one more to make it 11. Ten is never acceptable — these go to eleven.

## Confirmed wiring (all CONFIRMED 2026-06-15)

**Battery:** LS14250 + → B+ (right pos 13), − → B− (left pos 13). Through a connector. Never USB while cell is connected.

**DS18B20:** red → B+, black → B−, yellow → P0.24 (left pos 5). 4.7kΩ pull-up between yellow and red (data to VDD, not GND).

**Battery voltage divider:** B+ → 1MΩ → P0.02/A0 (right pos 6) → 1MΩ → GND. Empirical scale: `BATT_SCALE = 0.0004434` (B+=3.56V @ raw≈8030, 14-bit ADC).

**Debug serial:** board TX (left pos 12 / P0.06) → CP2102 RX. Board GND → CP2102 GND. P1.06 (left pos 1) → CP2102 VCC reference (driven HIGH in firmware). CP2102 TX pin disconnected. 115200 baud.

**Avoid:** P0.14, P0.16 (crash-loop), P0.13 (not on header), VCC/right pos 9 (0V on battery).

Full pinout table and detailed notes: `docs/hardware/teyleten-nrf52840-promicro.md`. Replication guide: `README.md`.

## Code structure
- `firmware/freezer_monitor/freezer_monitor.ino` — main Arduino sketch: DS18B20 temp, battery voltage (P0.02 divider), BTHome v2 BLE advertisement, 5-min sleep cycle. Firmware complete.
- `firmware/board_bringup/board_bringup.ino` — diagnostic sketch from P0.13 rail/identity test (resolved). Historical reference only.
- `gen_freezer_netlist.py` — data-driven KiCad netlist generator for the carrier PCB (v1.1.0). Edit `COMPONENTS`/`NETS` dicts and rerun to regenerate `freezer_monitor.net`. Includes a sanity check.
- `gen_nicenano_footprint.py` — footprint generator for the Teyleten module; emits `nice_nano_teyleten.kicad_mod`. Mounting it rotated 180° on the carrier is a pcbnew placement choice (R key) — not a separate footprint/netlist. See [[no-flipped-footprint-variant]].
- `freezer_monitor.net` — generated KiCad netlist (v1.1.0). Do not hand-edit; regenerate via `gen_freezer_netlist.py`.
- `ha-bridge/` — Theengs Gateway docker-compose config (fallback BLE→MQTT bridge if direct HA BT can't reach the freezer).
- `docs/` — reference documentation (Home Assistant REST API, BTHome spec, board hardware notes).

## User preferences
- Architecture: nRF52840 + DS18B20 + LS14250 → BTHome v2 over BLE → HA native BTHome integration (direct). Theengs Gateway on NAS = fallback for range issues only.
- Firmware framework: Arduino via Adafruit nRF52 BSP.
- Hardware: enthusiast carrier PCB (nRF52840 socketed in machine-pin headers, JST connectors for all peripherals, passives on-board). Netlist generated by `gen_freezer_netlist.py`.
- External alerting plan: GCP server receives push events from HA/ESP32 bridges and dispatches voip.ms SMS/calls per a configurable per-site rule list. In design phase — see "External alerting system" below.
- The end user will manage all git actions. Do not request to perform any git actions.
- This is a personal project — do not log time to the daily-log repo for it.

## External alerting system (in design)
Not yet implemented — design-only as of 2026-06-18, captured here so it isn't lost between sessions. Motivation: deploy this for family members too (Kyle's freezer, Sheila's freezer), not just personal use, so the design is multi-tenant from the start.

- **Two ingestion paths, one contract:** HA (webhook automation on BTHome state change) and a standalone ESP32 BLE bridge (for homes without HA) both POST the same shape to one API: `{site_id, temperature, battery, timestamp}`.
- **Two alert families:** heartbeat/watchdog (missing check-ins, a proxy for power/connectivity failure — there's no direct power sensor) vs condition alerts (temp-over-setpoint, battery-low; only meaningful while the device is actively reporting).
- **Heartbeat math, no event log:** store one `last_seen_at` per site; checker compares `now - last_seen_at` against `expected_interval_minutes * missing_events_threshold`. No historical check-in log needed for alerting — could be added later purely as an optional diagnostic.
- **Per-site rules are a uniform, variable-length list**, not fixed scalar fields. All three metrics (`battery_pct`, `temp_delta_c`, `missing_events`) share one rule shape: `{id, metric, threshold, action, repeat}`. Lets Kyle run 5 battery tiers while Sheila runs 2, with one rule-evaluation mechanism instead of per-metric special cases.
  - Rule `id` is stable and independent of list position — runtime open/resolved alert-state is keyed by `(site_id, rule_id)`.
  - Comparison direction is hardcoded per metric, not configurable: `battery_pct` triggers below threshold; `temp_delta_c`/`missing_events` trigger above.
  - Rules on the same metric don't suppress each other — at 4% battery, a 30%-threshold rule and a 5%-threshold rule are both independently true and each fires on its own schedule.
- **Re-alerting via `repeat`:** `once` (fire on first trip, suppress until resolved) or `every_Nh` (re-fire every N hours while still triggered). "Once" is just `repeat` with an infinite cooldown, not a separate code path.
- **Config:** simple hand-edited YAML, one entry per site (owner, contact, expected_interval, setpoint, rules list) — not a database/admin UI. Runtime state (`last_seen_at`, per-rule open/resolved + last-alerted-at) is separate from this file.
- **API key lives at the bridge, not in BTHome:** BLE advertisements broadcast in the clear, and HA would surface a Text/Raw BTHome object as a plaintext sensor in its own history — plus there's no spare room in the ~31-byte legacy advertising payload anyway. Key is baked into ESP32 bridge firmware/config, or held as an HA secret used by the forwarding automation. TLS required for the API regardless of bridge type.

Example `sites.yaml` shape:
```yaml
sites:
  - id: FreezerMonitor-Kyle
    owner: Kyle
    phone: "+1..."
    expected_interval_minutes: 5
    setpoint_c: -18
    rules:
      - {id: missing_10, metric: missing_events, threshold: 10, action: call, repeat: every_1h}
      - {id: temp_5,      metric: temp_delta_c,   threshold: 5,  action: call, repeat: every_1h}
      - {id: battery_30,  metric: battery_pct,    threshold: 30, action: sms,  repeat: once}
      - {id: battery_15,  metric: battery_pct,    threshold: 15, action: sms,  repeat: once}
      - {id: battery_5,   metric: battery_pct,    threshold: 5,  action: call, repeat: every_1h}
```

Open/undesigned: exact `/events` and `/check` endpoint contracts, ESP32 bridge firmware specifics, voip.ms integration specifics, whether to send an "all-clear" notification on alert resolution.

## Known edge cases handled
- DS18B20 is always-on (wired to `B+`/`B-` directly) — no power-gating, since P0.13 (the planned switch pin) isn't accessible on this board and the idle-current cost is negligible against the LS14250's capacity.
- **CONFIRMED 2026-06-15**: DS18B20 (red→B+, black→B-, yellow→P0.24 + 4.7k pull-up to B+) gives real readings via `firmware/freezer_monitor/freezer_monitor.ino`, observed over Serial1 + CP2102 adapter (~26°C in a warm basement, settling down from hand-warmth on the probe). Confirms `B+`/`B-` power, P0.24 OneWire data, and the Serial1+adapter debug workflow all work end-to-end.
- **CONFIRMED 2026-06-15**: BLE advertisement decodes correctly end-to-end (verified with a generic BLE Scanner app's raw-data view) — UUID 0xFCD2, device info 0x40, ascending object IDs (packet id, battery=100%, temperature matching the live DS18B20 reading). Full pipeline DS18B20 -> firmware -> BTHome v2 -> BLE advertisement is working.
- **CONFIRMED 2026-06-15**: first `requestTemperatures()`/`getTempCByIndex()` right after `sensors.begin()` reliably returns -127 (DEVICE_DISCONNECTED_C). Fixed with a throwaway read in `setup()` before `loop()` starts — verified by pulling and reinserting the battery: all readings valid immediately, no -127.
- **CONFIRMED 2026-06-15**: battery voltage via the external P0.02 divider tracks real changes accurately — a voltage dip from connecting a load and recovery afterward both showed up correctly in `readBatteryVoltage()`. `readBatteryPercent()` does a linear map between `BATT_FULL_V` (3.6V) and `BATT_EMPTY_V` (2.0V), reads near-100% for most of LS14250's life, falls quickly near the cliff.
- **CONFIRMED 2026-06-16**: HA native BTHome integration discovered `FreezerMonitor` within seconds on an N95 NUC with onboard BT. No Theengs Gateway needed under normal range conditions.
- **CONFIRMED 2026-06-16**: chest freezer lid attenuates signal from -54 dBm to -82/-88 dBm. TX power bumped to +8 dBm (nRF52840 max) — impact on battery life is negligible (~0.5 mAh/year extra).
- **CONFIRMED 2026-06-19**: [k-meeks/linux_bt_proxy](https://github.com/k-meeks/linux_bt_proxy) (forked, bug-fixed by user) deployed on a Linux host near the freezer as the active BT→HA bridge — reliably relays BTHome events despite the lid attenuation above. Theengs Gateway remains an untested fallback if this proxy path ever has issues.
- **Carrier PCB netlist** (2026-06-16): `gen_freezer_netlist.py` v1.1.0 generates KiCad-importable `freezer_monitor.net`. Key fix in v1.1.0: U1 B- must be explicitly tied to GND net — the `Module:nice_nano_v2` footprint defines B- as a separate named pad, not just another GND pin. Pad names in the netlist must match footprint pad names exactly (verify before import).
- **Carrier PCB (ordered 2026-06-18)**: The manufactured board uses `nice_nano_teyleten_usb_flipped` as the U1 footprint (per pcb_build .rpt). The generator scripts reference `nice_nano_teyleten` — this discrepancy only matters if you re-import the netlist into the existing KiCad project. Board is awaiting delivery for assembly and testing.

## Development process
Standard reminder: update this file after every bugfix or feature addition, capturing new edge cases, changed logic/external behavior, and new options/flags. Keep entries terse — this file is a reference, not documentation.
