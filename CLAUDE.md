# Freezer Monitor

## What this project is
A battery-powered temperature monitor that lives inside a chest freezer. An nRF52840 reads a DS18B20 temperature sensor and broadcasts the reading over BLE using the BTHome v2 format. Home Assistant picks it up directly via its built-in BTHome integration (native BT on the HA host — no gateway required). Theengs Gateway on a nearby NAS is a documented fallback for range issues. Power comes from a Saft LS14250 Li-SOCl2 cell (3.6V, primary/non-rechargeable) that is manually replaced when depleted — battery life is the dominant design constraint throughout. A carrier PCB design (KiCad netlist) is in progress to replace hand-wired headers with proper JST connectors and on-board passives.

Personal project. No git actions requested from Claude (user manages git). No daily-log time tracking for this project.

## Usage
Firmware confirmed working end-to-end. Build setup:

1. Arduino IDE > Preferences > Additional Boards Manager URLs, add:
   - `https://adafruit.github.io/arduino-board-index/package_adafruit_index.json`
   - `https://github.com/jpconstantineau/Community_nRF52_Arduino/releases/latest/download/package_jpconstantineau_boards_index.json`
2. Boards Manager: install "Adafruit nRF52", then "Community Add on Adafruit nrf52 boards".
3. Select board: **Nice Keyboard's nice!nano** (`nice_nano`, from Community package) — CONFIRMED correct for this clone.
4. Install libraries: `OneWire`, `DallasTemperature` (Bluefruit BLE comes with the Adafruit nRF52 core).
5. Open `firmware/freezer_monitor/freezer_monitor.ino`, build, flash via UF2 bootloader (double-tap RST).
6. **Before deployment:** set `SLEEP_INTERVAL_MS` back to `(5UL * 60UL * 1000UL)` — currently `1UL * 1000UL` (1s) for testing.

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
- **Chest freezer lid attenuates BLE signal significantly** — confirmed 2026-06-16: signal drops from -54 dBm on desk to -82/-88 dBm in basement when device is inside freezer. TX power bumped to max (+8 dBm) to compensate. Theengs Gateway on nearby NAS is the fallback if direct BT remains marginal. An ESP32 BT proxy on top of the freezer is the other fallback.
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
- `firmware/freezer_monitor/freezer_monitor.ino` — main Arduino sketch: DS18B20 temp, battery voltage (P0.02 divider), BTHome v2 BLE advertisement, 5-min sleep cycle. **`SLEEP_INTERVAL_MS` is currently 1s (testing) — restore to 5 min before deployment.**
- `firmware/board_bringup/board_bringup.ino` — diagnostic sketch from P0.13 rail/identity test (resolved). Historical reference only.
- `gen_freezer_netlist.py` — data-driven KiCad netlist generator for the carrier PCB (v1.1.0). Edit `COMPONENTS`/`NETS` dicts and rerun to regenerate `freezer_monitor.net`. Includes a sanity check.
- `gen_freezer_netlist_usb_flipped.py` — alternate netlist generator targeting a flipped module-footprint orientation (USB/B+/B- end on the opposite side). Writes `freezer_monitor_usb_flipped.net` and expects footprint `nice!nano clone:nice_nano_teyleten_usb_flipped`.
- `gen_nicenano_footprint.py` — footprint generator for the Teyleten module; now emits both `nice_nano_teyleten.kicad_mod` and `nice_nano_teyleten_usb_flipped.kicad_mod` in one run.
- `freezer_monitor.net` — generated KiCad netlist (v1.1.0). Do not hand-edit; regenerate via `gen_freezer_netlist.py`.
- `ha-bridge/` — Theengs Gateway docker-compose config (fallback BLE→MQTT bridge if direct HA BT can't reach the freezer).
- `docs/` — reference documentation (Home Assistant REST API, BTHome spec, board hardware notes).

## User preferences
- Architecture: nRF52840 + DS18B20 + LS14250 → BTHome v2 over BLE → HA native BTHome integration (direct). Theengs Gateway on NAS = fallback for range issues only.
- Firmware framework: Arduino via Adafruit nRF52 BSP.
- Hardware: enthusiast carrier PCB (nRF52840 socketed in machine-pin headers, JST connectors for all peripherals, passives on-board). Netlist generated by `gen_freezer_netlist.py`.
- External alerting plan: GCP server receives HA heartbeats; triggers voip.ms SMS + voice call on silence (HA down/power out) or threshold breach (temp too high, battery low, sensor unavailable). In design phase.
- The end user will manage all git actions. Do not request to perform any git actions.
- This is a personal project — do not log time to the daily-log repo for it.

## Known edge cases handled
- DS18B20 is always-on (wired to `B+`/`B-` directly) — no power-gating, since P0.13 (the planned switch pin) isn't accessible on this board and the idle-current cost is negligible against the LS14250's capacity.
- **CONFIRMED 2026-06-15**: DS18B20 (red→B+, black→B-, yellow→P0.24 + 4.7k pull-up to B+) gives real readings via `firmware/freezer_monitor/freezer_monitor.ino`, observed over Serial1 + CP2102 adapter (~26°C in a warm basement, settling down from hand-warmth on the probe). Confirms `B+`/`B-` power, P0.24 OneWire data, and the Serial1+adapter debug workflow all work end-to-end.
- **CONFIRMED 2026-06-15**: BLE advertisement decodes correctly end-to-end (verified with a generic BLE Scanner app's raw-data view) — UUID 0xFCD2, device info 0x40, ascending object IDs (packet id, battery=100%, temperature matching the live DS18B20 reading). Full pipeline DS18B20 -> firmware -> BTHome v2 -> BLE advertisement is working.
- **CONFIRMED 2026-06-15**: first `requestTemperatures()`/`getTempCByIndex()` right after `sensors.begin()` reliably returns -127 (DEVICE_DISCONNECTED_C). Fixed with a throwaway read in `setup()` before `loop()` starts — verified by pulling and reinserting the battery: all readings valid immediately, no -127.
- **CONFIRMED 2026-06-15**: battery voltage via the external P0.02 divider tracks real changes accurately — a voltage dip from connecting a load and recovery afterward both showed up correctly in `readBatteryVoltage()`. `readBatteryPercent()` does a linear map between `BATT_FULL_V` (3.6V) and `BATT_EMPTY_V` (2.0V), reads near-100% for most of LS14250's life, falls quickly near the cliff.
- **CONFIRMED 2026-06-16**: HA native BTHome integration discovered `FreezerMonitor` within seconds on an N95 NUC with onboard BT. No Theengs Gateway needed under normal range conditions.
- **CONFIRMED 2026-06-16**: chest freezer lid attenuates signal from -54 dBm to -82/-88 dBm. TX power bumped to +8 dBm (nRF52840 max) — impact on battery life is negligible (~0.5 mAh/year extra). Theengs Gateway / ESP32 BT proxy are fallbacks if signal remains marginal.
- **Carrier PCB netlist** (2026-06-16): `gen_freezer_netlist.py` v1.1.0 generates KiCad-importable `freezer_monitor.net`. Key fix in v1.1.0: U1 B- must be explicitly tied to GND net — the `Module:nice_nano_v2` footprint defines B- as a separate named pad, not just another GND pin. Pad names in the netlist must match footprint pad names exactly (verify before import).
- **Footprint flip semantics** (2026-06-16): `nice_nano_teyleten_usb_flipped.kicad_mod` must be generated as a true 180-degree rotation (swap sides + reverse order), not a top/bottom mirror. Correct result puts `B+` at bottom-left and `B-` at bottom-right in the flipped variant.

## Development process
Standard reminder: update this file after every bugfix or feature addition, capturing new edge cases, changed logic/external behavior, and new options/flags. Keep entries terse — this file is a reference, not documentation.
