# Teyleten Pro Micro nRF52840 (nice!nano v2 clone)

Saved: 2026-06-15. Compiled from web research — items marked **UNVERIFIED** have not
yet been confirmed against the actual board and should be checked once hardware is
in hand. Move confirmed items to CLAUDE.md's "confirmed quirks" section once tested.

## Identity

- Sold as "Teyleten Robot Pro Micro NRF52840", ~$4, nice!nano v2 form-factor clone.
- Generic family also known as "SuperMini nRF52840" / "Pro Micro nRF52840".
- Zephyr board name for this family: `promicro_nrf52840` (marked "not actively
  maintained" — treat as a loose reference, not gospel).
- Ships with Adafruit's UF2 bootloader.

## Sources

- Pinout notes (community-tested): https://github.com/longrackslabs/teyleten-nrf52840-pinout
- Zephyr board doc: https://docs.zephyrproject.org/latest/boards/others/promicro_nrf52840/doc/index.html
- nice!nano pinout/schematic: https://nicekeyboards.com/docs/nice-nano/pinout-schematic/
- nice!nano battery measurement differences (v1 vs v2): https://github.com/joric/nrfmicro/wiki/Batteries
- Community Arduino board package: https://github.com/jpconstantineau/Community_nRF52_Arduino

## Arduino IDE setup

1. Add both URLs to **File > Preferences > Additional Boards Manager URLs**:
   - `https://adafruit.github.io/arduino-board-index/package_adafruit_index.json` (official Adafruit nRF52 core — required base package)
   - `https://github.com/jpconstantineau/Community_nRF52_Arduino/releases/latest/download/package_jpconstantineau_boards_index.json` (community add-on, adds nice!nano-family boards)
2. In Boards Manager, install **Adafruit nRF52** first, then the community package
   listed as **"Community Add on Adafruit nrf52 boards"** — it appears at the bottom
   of the board list.
3. **CONFIRMED (2026-06-15)**: select **"Nice Keyboard's nice!nano"** (`nice_nano`,
   from `community_nrf52` package v0.1.21). This matches the Teyleten board's
   physical Pro Micro/nice!nano form factor and its `variant.h` defines a `PIN_VBAT`
   (see Battery section below). Build settings: `nice_nano.build.vid=0x239A`,
   `pid=0x00B3`, `upload.maximum_size=815104`.
4. **CONFIRMED**: the board's bootloader reports via USB as VID `0x239A` / PID
   `0x8029` (Tools > Get Board Info shows "Adafruit Feather nRF52840 Express") —
   this exactly matches the `feather52840` entry in the Adafruit package. Despite
   the declared PID differing from `nice_nano`'s (`0x00B3`), both boards use
   `upload.tool=nrfutil` with the same `upload.maximum_size=815104` (same SoftDevice
   S140 6.1.1 layout), so selecting `nice_nano` for build/upload should still work —
   the 1200bps-touch DFU reset doesn't depend on the declared PID matching. If
   upload fails, fall back to building as `feather52840` and only use `nice_nano`
   for the variant.h pin reference.
5. To flash: double-tap the reset button to enter UF2 bootloader mode (status LED
   fades in/out when active), then upload from Arduino IDE (or drag-and-drop the
   `.uf2`).

## Pin numbering convention

From community pin-discovery testing, **confirmed** by the `nice_nano` variant.h
(`_PINNUM(port, pin) = port*32 + pin`):
- `P0.xx` = Arduino pin number `xx` (for xx = 0–31)
- `P1.xx` = Arduino pin number `32 + xx` (for xx = 0–15, i.e. Arduino pins 32–47)

## `nice_nano` variant.h pin reference (confirmed, from installed package v0.1.21)

- `PIN_LED1` (blue) = P0.15 = pin 15 — matches Zephyr `promicro_nrf52840` LED0.
- `PIN_VBAT` = `A7` = pin 31 (P0.31) — see Battery section below.
- Analog: A0-A3 = pins 2-5 (P0.02-P0.05), A4-A7 = pins 28-31 (P0.28-P0.31). `PIN_AREF` = pin 2 (shared with A0).
- Serial1: RX = pin 8 (P0.08), TX = pin 6 (P0.06)
- SPI: MISO = pin 43 (P1.11), MOSI = pin 10 (P0.10), SCK = pin 45 (P1.13)
- Wire: SDA = pin 17 (P0.17), SCL = pin 20 (P0.20)
- NFC1/NFC2 = P0.09 / P0.10 (shared with SPI MOSI when NFC disabled)
- BUTTON_1 = P0.18 marked "unusable: RESET"; BUTTON_2 = P0.19 "no connection" — avoid both.
- `ADC_RESOLUTION` = 14 bits.

## Quick pin reference (silkscreen label -> function)

The silkscreen prints the raw `P0.xx`/`P1.xx` number (with leading zeros, no
"P0." prefix) — e.g. the pin labeled `006` is P0.06. There are no TX/RX/A0-style
function labels printed on the board. For functions used in this project:

| Silkscreen label | Pin / function |
|---|---|
| `B+` | Battery positive (LS14250 +) |
| `B-` | Battery negative (LS14250 -) |
| `006` | P0.06 = `Serial1` TX (debug UART, see below) |
| `008` | P0.08 = `Serial1` RX |
| `007` | P0.07 = OneWire/DS18B20 data (firmware `ONEWIRE_PIN`) |
| `013` | P0.13 = sensor rail power switch (firmware `SENSOR_PWR_PIN`) |
| `031` | P0.31 = A7 = `PIN_VBAT` candidate |
| `VCC` | Regulated 3.3V output |
| `RAW` | Unregulated USB-side rail (not `B+` — don't confuse) |
| `GND` | Ground (multiple) |
| (not exposed) | P0.04 = A2 = alternate VBAT candidate (internal only) |

## Physical board pinout (CONFIRMED 2026-06-15, from board photos)

Top side (USB-C connector), bottom edge of header, right-to-left from the
connector corner: **`B+`**, `RAW`, `GND`, `RST`, `VCC`, `031`, `029`, `002`, ...
Top edge of header, same corner: **`B-`**, `006`, `008`, `GND`, `GND`, `017`, ...

- **`B+` / `B-`** — the battery connection pads. This is the only battery input
  exposed on this board (no separate charge-bypass pad). See Battery section
  below for wiring and safety implications.
- **`RAW`** — unregulated USB-side rail (VBUS-derived), distinct from `B+`. Do
  not confuse the two.
- **`VCC`** — regulated 3.3V output.
- **`031`** = P0.31 = `PIN_VBAT`/A7 (matches variant.h, see Battery voltage
  monitoring section).
- Back side of the board has a 4-pad cluster silkscreened `GND` / `CLK` / (one
  more) / `VDD` near the top edge — likely a debug/SWD header. Not needed for
  current work; useful if firmware debugging via SWD is ever required.

## Physical pin reference (1-13 per side)

Simpler than reading silkscreen labels: each header row has 13 pins. **Pin 1 =
the end farthest from the USB-C connector, pin 13 = the `B-`/`B+` pad itself.**

| Pos | Left side (B- side) | Right side (B+ side) |
|---|---|---|
| 1 | P1.06 — GPIO, no special function | P0.09 — GPIO / NFC1 |
| 2 | P1.04 — GPIO, no special function | P0.10 — GPIO / NFC2, SPI MOSI |
| 3 | P0.11 — GPIO, no special function | P1.11 — SPI MISO |
| 4 | P1.00 — GPIO, no special function | P1.13 — SPI SCK |
| 5 | P0.24 — GPIO, no special function | P1.15 — GPIO, no special function |
| 6 | P0.22 — GPIO, no special function | P0.02 — A0 / AREF |
| 7 | P0.20 — I2C SCL | P0.29 — A5 |
| 8 | P0.17 — I2C SDA | P0.31 — A7 / `PIN_VBAT` |
| 9 | GND | VCC — regulated 3.3V output (USB/RAW-derived, see below) |
| 10 | GND | RST — reset |
| 11 | P0.08 — Serial1 RX | GND |
| 12 | P0.06 — Serial1 TX | RAW — unregulated USB/VBUS rail |
| 13 | **B-** — battery negative | **B+** — battery positive |

Notes:
- P0.15 (`PIN_LED1`, onboard blue LED) is not in this table — it's an onboard
  component, not broken out to a header pin.
- P0.13 also doesn't appear in this table — see "Known special pins" below.
  P0.07 (the original OneWire pin choice) had the same problem; firmware now
  uses P0.24 (left side, position 5) instead.

## Known special pins

- **P0.13** — **CONFIRMED 2026-06-15: not broken out on this board's header at
  all.** `digitalWrite(13, ...)` has no observable effect on `VCC` or any
  header pin (tested via `firmware/board_bringup/board_bringup.ino`: B+ read
  3.6V correctly via multimeter, confirming the meter/ground setup was good,
  but `VCC` stayed near 0V regardless of P0.13 state, and right-side positions
  3-5 all read flat ~45mV noise regardless of P0.13 state). Originally planned
  as `SENSOR_PWR_PIN` for DS18B20 power-gating — dropped; DS18B20 now wires
  directly to `B+`/`B-`.
- **P0.14, P0.16** — **CONFIRMED 2026-06-15: both hang/crash-loop the board**
  as soon as either is configured as GPIO (`pinMode`/`digitalWrite`). Do not
  use either pin.
- **`VCC` (right side, position 9)** — **CONFIRMED 2026-06-15: reads ~0V when
  running off `B+` alone**, regardless of P0.13 state. Likely fed from a
  USB/RAW-derived regulator rather than the battery — not usable as a
  peripheral supply rail on battery power.
- **LED0 = P0.15** (per Zephyr `promicro_nrf52840` board doc) — onboard only,
  not a header pin.

## Battery cell: Saft LS14250 (Li-SOCl2, primary/non-rechargeable)

**CONFIRMED 2026-06-15**: the cell in use is a Saft LS14250 — Lithium Thionyl
Chloride, 1/2AA, 3.6V nominal, primary (non-rechargeable). This is NOT the
Li-ion/LiPo chemistry the onboard charge IC (e.g. BQ24072 on nice!nano-family
boards) expects.

- **Do not let the onboard charge circuit attempt to charge this cell.** Li-SOCl2
  cells can vent, rupture, or ignite under reverse/charge current — this is a
  safety issue, not just a degradation one.
- **CONFIRMED 2026-06-15**: `B+`/`B-` (see "Physical board pinout" above) is the
  only battery input on this board — there is no separate charge-bypass pad.
  Charging only engages when USB power is present (the charge IC is powered from
  VBUS), so the operating rule is: **never plug in USB while the LS14250 is
  connected to B+/B-**. Wire the cell through a connector (JST pigtail + holder
  or a 2-pin header), not a permanent solder joint, so it can be unplugged before
  any USB connection (reprogramming, debugging).
- Wiring: **LS14250 positive lead → `B+`, negative lead → `B-`**. Double-check
  polarity against the cell's own markings before connecting — reverse polarity
  into a charge IC input is its own hazard.

### Debugging while battery-powered

The board's own `Serial` (USB CDC) is only usable when its USB port is
connected — which conflicts with the LS14250-on-`B+`/`B-` rule above. For any
test that needs the battery actually powering the board (e.g. reading
`PIN_VBAT`/A2 against a real battery voltage), use **`Serial1`** (hardware
UART, TX = pin 6/P0.06) wired to a separate 3.3V USB-to-serial adapter
(FTDI/CP2102/CH340): board TX → adapter RX, GND → GND, adapter power pin left
disconnected. The adapter gets its own USB connection to the PC; the board
stays on battery only. `firmware/board_bringup/board_bringup.ino` prints to
both `Serial` and `Serial1` for this reason.

### Programming workflow with the LS14250 connected

Because `B+`/`B-` is the charge IC's input, flashing (which requires USB) and
running on the LS14250 can't happen at the same time. Workflow:

1. Disconnect the LS14250 from `B+`/`B-`.
2. Connect USB, flash firmware.
3. Disconnect USB.
4. Reconnect the LS14250 to run standalone.

**CONFIRMED 2026-06-15**: with only the LS14250 on `B+`/`B-` (no USB, no
firmware flashed yet), the board powered up and a red LED (near a GND pin —
not near the USB connector/charge IC) slow-flashed. This is consistent with
the UF2 bootloader's idle pattern on a board with no application yet, and
confirms `B+`/`B-` wiring powers the board correctly. Not a charge-IC fault
indicator — that would be expected near the USB connector and requires USB
power to occur at all.

Wire the battery through a connector (2-pin header + jumper, or JST pigtail),
not a permanent solder joint, so steps 1 and 4 are quick during development.
- "Recharge" is replaced by "swap the cell" for this project. LS14250 has very
  low self-discharge and is commonly used in devices needing years of service
  from one cell (water meters, alarms), so this is a reasonable tradeoff.
- Li-SOCl2 has a very flat discharge voltage curve until near end-of-life, then
  drops sharply. A voltage-based battery % will read near-100% for most of the
  cell's life and then fall quickly — see [[project-failure-alerting]] for how
  this affects alerting design, and "Battery voltage monitoring" below for how
  it's measured on this board.

## Battery voltage monitoring

- **CONFIRMED 2026-06-15**: `PIN_VBAT`/A7 (P0.31) and A2 (P0.04) are both
  floating/unconnected on this clone — `analogRead()` on either returns pure
  noise uncorrelated with actual battery voltage. There is no internal VBAT
  divider on this board.
- **Solution: external resistor divider.** Two ~1MΩ resistors in series from
  `B+` to `GND`, midpoint wired to `P0.02`/A0 (right side, position 6). Per
  https://devzone.nordicsemi.com/nordic/nordic-blog/b/blog/posts/measuring-lithium-battery-voltage-with-nrf52
  this is the standard approach when no internal divider is present. Adds
  ~1.8µA continuous draw — negligible against the LS14250's capacity.
- Calibrated empirically: with the divider wired, `analogRead(A0)` (14-bit,
  `analogReadResolution(14)`) averaged ~8030 (range 7984-8076) while a
  multimeter read B+ = 3.56V. `BATT_SCALE = 3.56 / 8030 ≈ 0.0004434` V/count —
  see `firmware/freezer_monitor/freezer_monitor.ino`. This single empirical
  constant absorbs both the divider ratio and the ADC reference, so exact
  resistor tolerances and reference voltage don't need to be known.
- `readBatteryVoltage()` averages 8 samples to smooth ~1% ADC noise.
  `readBatteryPercent()` linearly maps `BATT_FULL_V` (3.6V) to `BATT_EMPTY_V`
  (2.0V) — appropriate for the LS14250's flat-then-cliff discharge curve, see
  [[project-failure-alerting]].
