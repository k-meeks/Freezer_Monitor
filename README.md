# Freezer Monitor

A battery-powered sensor that lives inside a chest freezer and reports temperature to Home Assistant via Bluetooth.

## How it works

1. An **nRF52840** wakes on a timer, reads a **DS18B20** temperature sensor, measures battery voltage via an external resistor divider, and broadcasts both as a **BTHome v2** Bluetooth Low Energy advertisement.
2. **Home Assistant** (with a Bluetooth adapter) picks up the advertisement directly via its built-in BTHome integration — no gateway required if HA has BT access near the freezer.
3. HA exposes temperature and battery as entities for dashboards, automations, and alerting.

Power comes from a single Saft LS14250 cell (Li-SOCl₂, 3.6V, 1/2AA) — non-rechargeable, replaced manually when depleted.

## Status

Firmware complete and confirmed working end-to-end. HA native BTHome integration discovers the device within seconds — no gateway required with a Bluetooth-capable HA host.

**Before deploying:** `SLEEP_INTERVAL_MS` in the sketch is currently `1s` (testing) — change to `(5UL * 60UL * 1000UL)` before final installation.

**Range note:** Chest freezer lids significantly attenuate BLE. TX power is set to +8 dBm (nRF52840 max). If HA still can't see the device reliably from inside the freezer, place an [ESPHome Bluetooth proxy](https://esphome.io/components/bluetooth_proxy.html) (cheap ESP32) on top of the freezer, or use the Theengs Gateway fallback in `ha-bridge/`.

A carrier PCB design is in progress — see [Carrier PCB](#carrier-pcb) below.

---

## Parts list

| Part | Spec / notes |
|---|---|
| nRF52840 board | Teyleten Pro Micro nRF52840 (nice!nano v2 clone, ~$4) |
| Temperature sensor | DS18B20 (waterproof probe recommended for freezer use) |
| Battery | Saft LS14250 — Li-SOCl₂, 3.6V nominal, 1/2AA, **primary/non-rechargeable** |
| Battery holder | 1/2AA holder with leads, or JST pigtail — wire through a connector, not direct solder |
| Pull-up resistor | 4.7kΩ (DS18B20 data line) |
| Divider resistors | 2× ~1MΩ (battery voltage sense) |
| Debug adapter | CP2102 or CH340 USB-to-serial, 3.3V logic (development only) |

---

## Board pinout

The board has two 13-pin header rows. **Pin 1 = end farthest from the USB-C connector. Pin 13 = the B−/B+ battery pad itself.**

```
                    USB-C connector
                         |||
         Left (B− side)       Right (B+ side)
         ──────────────       ───────────────
  13     B−  ←battery−        B+  ←battery+       13
  12     P0.06  Serial1 TX    RAW  (USB rail)      12
  11     P0.08  Serial1 RX    GND                  11
  10     GND                  RST  (reset)         10
   9     GND                  VCC  (unusable on    9
                                    battery only)
   8     P0.17  I2C SDA       P0.31 / A7           8
   7     P0.20  I2C SCL       P0.29 / A5           7
   6     P0.22                P0.02 / A0  ←divider 6
   5     P0.24  ←DS18B20      P1.15                5
   4     P1.00                P1.13  SPI SCK        4
   3     P0.11                P1.11  SPI MISO       3
   2     P1.04                P0.10  NFC2/SPI MOSI  2
   1     P1.06                P0.09  NFC1            1
```

**Known-bad pins — do not use:**
- P0.14, P0.16: hang/crash-loop the board when configured as GPIO
- P0.13: not connected to any header pin on this board
- VCC (right pos 9): reads ~0V when running on battery only

---

## Wiring

### Battery (LS14250)

```
LS14250 +  →  B+  (right side, pos 13)
LS14250 −  →  B−  (left side, pos 13)
```

> **Safety:** The board's onboard charge IC is wired to B+/B−. Li-SOCl₂ cells
> must never receive charge current — this is a fire/rupture hazard.
> **Never connect USB while the LS14250 is wired to B+/B−.**
> Wire the cell through a connector (header pins, JST) so it can be unplugged
> before any USB connection.

---

### DS18B20 temperature sensor

The DS18B20 probe has three wires:

```
Red   (VDD)   →  B+  (right side, pos 13)
Black (GND)   →  B−  (left side, pos 13)
Yellow (data) →  P0.24  (left side, pos 5)

4.7kΩ pull-up resistor between yellow (data) and red (VDD/B+)
  — NOT to GND. The data line must be pulled up to VDD, not ground.
```

The easiest way to install the pull-up: bridge the resistor between the yellow
and red wires right at the point where they enter the board headers.

---

### Battery voltage divider

Two ~1MΩ resistors in series form a voltage divider from B+ to GND. The
midpoint is tapped to an ADC input so the firmware can read battery voltage.

```
B+  (right side, pos 13)
  │
 [1MΩ]
  │
  ├──→  P0.02 / A0  (right side, pos 6)
  │
 [1MΩ]
  │
GND  (left side, pos 9 or 10, or right side pos 11)
```

Practical assembly: twist the two resistors together end-to-end. One free end
goes to B+, the other free end goes to GND, and the junction (where they meet)
goes to P0.02/A0 (right side, pos 6).

Continuous draw: ~1.8µA — negligible against the LS14250's 1200mAh capacity.

---

### Debug serial (development only)

When debugging on battery (USB disconnected), use a CP2102/CH340 USB-to-serial
adapter wired to Serial1:

```
Board TX  (left side, pos 12 / P0.06)  →  Adapter RX
Board GND (left side, pos 9 or 10)     →  Adapter GND
Adapter TX pin                          →  leave disconnected
Adapter power/VCC pin                   →  leave disconnected
```

The adapter gets its own USB connection to the PC. The board stays on battery.
Baud rate: 115200.

---

## Arduino IDE setup

1. **File → Preferences → Additional Boards Manager URLs**, add both:
   - `https://adafruit.github.io/arduino-board-index/package_adafruit_index.json`
   - `https://github.com/jpconstantineau/Community_nRF52_Arduino/releases/latest/download/package_jpconstantineau_boards_index.json`
2. **Boards Manager**: install **Adafruit nRF52**, then **Community Add on Adafruit nrf52 boards**.
3. Select board: **Nice Keyboard's nice!nano** (from the Community package).
4. Install libraries: **OneWire**, **DallasTemperature** (Bluefruit BLE is included with the Adafruit nRF52 core).
5. Open `firmware/freezer_monitor/freezer_monitor.ino`.

---

## Programming workflow

Because B+/B− is the charge IC input, flashing and running on the LS14250
cannot happen at the same time:

1. Disconnect the LS14250 from B+/B−.
2. Connect USB, flash firmware from Arduino IDE.
3. Disconnect USB.
4. Reconnect the LS14250.

To enter the UF2 bootloader manually: double-tap the RST pin (right side,
pos 10) — the onboard LED will fade in/out when the bootloader is active.

---

## Home Assistant setup

1. Ensure HA has Bluetooth hardware (built-in adapter or an ESPHome BT proxy).
2. **Settings → Devices & Services → Add Integration → BTHome**.
3. HA will discover the device (`FreezerMonitor`) within a few seconds.
4. The device exposes: temperature (°C), battery (%), packet ID.

> **Range note:** Chest freezer metal lids significantly attenuate BLE signal.
> If HA can't see the device from inside the freezer, place a Bluetooth proxy
> (cheap ESP32 running ESPHome) on top of the freezer, or use Theengs Gateway
> on a nearby host to bridge BLE → MQTT → HA.

---

---

## Carrier PCB

A KiCad carrier board sockets the nRF52840 module into machine-pin headers; all peripherals connect via JST-PH connectors; passives (pull-up, voltage divider, bulk cap) are placed components on the board.

### Bill of materials

PCB-side components (driven by `COMPONENTS` in `gen_freezer_netlist.py`):

| Ref | Qty | Part | Value / spec | Package | Notes |
|---|---|---|---|---|---|
| U1 | 1 | nice!nano nRF52840 (Teyleten clone) | — | THT, 2×13 @ 2.54mm | Socketed, not soldered directly — see machine-pin headers below |
| BT1 | 1 | Battery holder | Keystone 1011, 1/2AA | THT | Polarity-keyed; footprint from SnapEDA (`pcb_build/1011/`) |
| R1, R2 | 2 | Resistor | 1MΩ | 0805 | Battery voltage divider |
| R3 | 1 | Resistor | 4.7kΩ | 0805 | DS18B20 OneWire pull-up to VBAT (not 3.3V) |
| C1 | 1 | Aluminum-polymer radial capacitor | 100µF, low-ESR/low-leakage, ≥6.3V | THT, 8mm dia, 3.5mm lead pitch | Bulk cap at the cell terminals — absorbs BLE TX current spikes against the LS14250's high internal impedance |
| C2 | 1 | Ceramic capacitor | 10nF | 0805 | ADC sense-node decoupling at P0.02 |
| J1 | 1 | JST PH receptacle, 3-pos | B3B-PH-K | THT, 2.00mm pitch | DS18B20 connector |
| J2 | 1 | Pin header, 1×4 | — | THT, 2.54mm | Debug UART: GND / VCC / TX / RX |
| JP1 | 1 | Pin header, 1×2 | — | THT, 2.54mm | Battery isolation jumper — pull before connecting USB |

Off-netlist items needed to finish the build:

| Item | Qty | Notes |
|---|---|---|
| Saft LS14250 cell | 1 | Drops into BT1 — see [Battery (LS14250)](#battery-ls14250) safety note |
| Machine-pin (turned-pin) header strip, 2.54mm | 2× 1×13 | Sockets for U1 so the module can be swapped without desoldering |
| 2.54mm jumper shunt | 1 | For JP1 |
| JST PH 3-pos plug + crimp pins (or pre-crimped pigtail) | 1 | Mates with J1 — only needed if your DS18B20 probe isn't already terminated with one |
| 2-pin or 4-pin 2.54mm header mate | 1 (optional) | For a CP2102/CH340 debug adapter — development only |

All SMD passives are 0805 to keep hand-soldering reasonable without hot air.

### Generating the design files

Regenerate the netlist after any connectivity change:

```
python3 gen_freezer_netlist.py
```

Regenerate the U1 footprint (only needed if the physical module's pinout or dimensions change):

```
python3 gen_nicenano_footprint.py
```

This writes `nice_nano_teyleten.kicad_mod`. To mount U1 rotated 180° (USB/B+/B- end at the opposite side of the board), rotate the footprint instance in pcbnew — that's a placement choice, not something the generator needs to encode.

**Key design decisions baked into the netlist:**
- `JP1` interrupts the battery positive rail — pull the jumper before connecting USB for reprogramming
- `R3` (4.7kΩ) pulls DS18B20 data to VBAT, not 3.3V — sensor is powered from the cell directly
- `C1` (100µF low-ESR electrolytic) at the cell terminals dampens the LS14250's high internal impedance under BLE TX bursts
- `C2` (10nF) decouples the ADC sense node at P0.02
- J2 pin 2 (VCC) is sourced from P1.06 held HIGH — provides a 3.3V logic reference for the CP2102 debug adapter without requiring VCC rail (which is unavailable on battery-only power)

> **Footprint warning:** The netlist uses functional pad names (`B+`, `B-`, `P0.24`, etc.) for U1. Verify these match the exact pad names in `nice!nano clone:nice_nano_teyleten` (or whatever footprint you assign to U1) before importing into KiCad — a mismatch silently drops the connection with no DRC error.

---

## External alerting (planned)

Not yet built — this section documents the intended design so it doesn't get lost between sessions.

**Goal:** when something silently goes wrong (power outage, dead battery, freezer warming up, or HA itself going down), get a phone call or text to a real person — not just a dashboard nobody's looking at.

**Architecture:**

```
nRF52840 (BTHome over BLE)
        │
        ├─ HA host w/ BT  ──┐
        │                   │   POST {site_id, temperature, battery, timestamp}
        └─ ESP32 BLE bridge ┘        (for homes without HA)
                            │
                            ▼
                Alerting API (GCP, TLS + API key)
                            │
                per-site rule evaluation
                            │
                      voip.ms (SMS / call)
```

Designed to scale beyond one freezer in one house — family members could each run their own monitor with their own contact info and thresholds.

**Per-site config** is a hand-edited YAML file, one entry per site, with a variable-length list of alert rules so each owner can have as many or as few thresholds as they want:

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

Each rule fires independently on its own schedule (`once`, or `every_Nh` to keep repeating until resolved), tracked per `(site_id, rule_id)` rather than list position, since rules can be added or reordered later.

**Two alert types:**
- **Heartbeat/watchdog** — missing check-ins, a proxy for power or connectivity failure (there's no direct power sensor). Needs no event log: one `last_seen_at` timestamp per site, compared against `expected_interval_minutes × threshold` cycles.
- **Condition alerts** — temperature too far above setpoint, or battery below a tier threshold. Only meaningful while the device is actively reporting.

**Auth:** the API key lives at the bridge (an HA secret, or baked into ESP32 bridge firmware/config) — never inside the BTHome BLE payload itself, since BLE advertisements broadcast in the clear and there's no spare room in the ~31-byte legacy advertising payload anyway. TLS is required for the API regardless of which bridge is talking to it.

**Still undecided:** exact `/events`/`/check` endpoint contracts, ESP32 bridge firmware specifics, voip.ms integration details, whether to send an "all-clear" notice when an alert resolves.

---

## Repository layout

```
firmware/
  freezer_monitor/     Main Arduino sketch (temperature + BTHome v2 advertisement)
  board_bringup/       Diagnostic sketch used during hardware bring-up (historical)
gen_freezer_netlist.py KiCad netlist generator for the carrier PCB
freezer_monitor.net    Generated KiCad netlist (regenerate via gen_freezer_netlist.py)
ha-bridge/             Theengs Gateway docker-compose (fallback if direct BT fails)
docs/
  bthome/              BTHome v2 format reference
  hardware/            Board pinout, confirmed quirks, battery notes
  home-assistant/      HA REST API reference
```
