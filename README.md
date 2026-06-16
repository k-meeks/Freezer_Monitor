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

A KiCad carrier board is in progress. The nRF52840 module sockets into machine-pin headers; all peripherals connect via JST-PH connectors; passives (pull-up, voltage divider, bulk cap) are placed components on the board.

Regenerate the netlist after any connectivity change:

```
python3 gen_freezer_netlist.py
```

If you want the module footprint orientation flipped so the USB/B+/B- end sits
at the opposite end of the board, generate the alternate netlist:

```
python3 gen_freezer_netlist_usb_flipped.py
```

This writes `freezer_monitor_usb_flipped.net` and expects a footprint named
`nice!nano clone:nice_nano_teyleten_usb_flipped` with the same pad names.

Generate module footprints (normal + flipped variants):

```
python3 gen_nicenano_footprint.py
```

This writes:
- `nice_nano_teyleten.kicad_mod`
- `nice_nano_teyleten_usb_flipped.kicad_mod`

The `usb_flipped` footprint is a true 180-degree rotation mapping (left/right
swap plus top/bottom reversal), not a simple mirror.

**Key design decisions baked into the netlist:**
- `JP1` interrupts the battery positive rail — pull the jumper before connecting USB for reprogramming
- `R3` (4.7kΩ) pulls DS18B20 data to VBAT, not 3.3V — sensor is powered from the cell directly
- `C1` (100µF low-ESR electrolytic) at the cell terminals dampens the LS14250's high internal impedance under BLE TX bursts
- `C2` (10nF) decouples the ADC sense node at P0.02
- J2 pin 2 (VCC) is sourced from P1.06 held HIGH — provides a 3.3V logic reference for the CP2102 debug adapter without requiring VCC rail (which is unavailable on battery-only power)

> **Footprint warning:** The netlist uses functional pad names (`B+`, `B-`, `P0.24`, etc.) for U1. Verify these match the exact pad names in your chosen `Module:nice_nano_v2` footprint before importing into KiCad — a mismatch silently drops the connection with no DRC error.

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
