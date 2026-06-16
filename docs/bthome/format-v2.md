# BTHome v2 Format Reference

Source: https://bthome.io/format/
Saved: 2026-06-15

## Overview

BTHome v2 is a Bluetooth Low Energy (BLE) advertising format released in November 2022. The format enables devices to transmit sensor data and events through BLE advertisements using a standardized packet structure.

## BLE Packet Structure

BLE packets consist of four components: preamble (1 octet), access address (4 octets), Protocol Data Unit (PDU) (2-257 octets), and Cyclic Redundancy Check (CRC) (3 octets). The actual data transmission occurs within the PDU payload.

## Advertising Payload Structure

The advertising payload comprises one or more **Advertising Data (AD) elements**. Each element contains:
- 1st byte: length (excluding the length byte)
- 2nd byte: AD type specifying the data category
- Remaining bytes: AD data with meaning defined by the AD type

### Required and Recommended Elements

A BTHome advertisement should include:
- **Service Data (16-bit UUID)** - Required, contains actual BTHome data
- **Flags** - Strongly recommended for proper parsing
- **Local Name** - Optional, aids device identification

### Flags Element (`0x01`)

The standard BTHome flags value is `020106`:
- `0x02` = length (2 bytes)
- `0x01` = Flags AD type
- `0x06` = bit pattern `00000110`
  - Bit 1: LE General Discoverable Mode
  - Bit 2: BR/EDR Not Supported

This element is particularly important for passive scanning compatibility with systems like Home Assistant's Bluetooth integration.

### Service Data Element (`0x16`)

Contains the actual BTHome payload with this structure:
- Length byte
- `0x16` = Service Data - 16-bit UUID type
- UUID (16-bit, little-endian)
- BTHome device information byte
- One or more measurements

### Local Name Elements

Optional AD elements for device identification:
- `0x08` = Shortened local name
- `0x09` = Complete local name

Example: `0B094449592D73656E736F72` decodes to "DIY-sensor"

## BTHome Data Format

BTHome service data contains three components:

### UUID Identifier

The 16-bit UUID `0xFCD2` (read in reverse byte order) identifies BTHome messages. This UUID is sponsored by Allterco Robotics (Shelly manufacturer) and is free to use under their license.

### Device Information Byte

The first byte after the UUID encodes device capabilities:

| Bit(s) | Field | Values |
|--------|-------|--------|
| 0 | Encryption flag | 0 = unencrypted, 1 = encrypted |
| 1 | Reserved | — |
| 2 | Trigger-based device flag | 0 = regular intervals, 1 = irregular intervals |
| 3-4 | Reserved | — |
| 5-7 | BTHome version | `010` = version 2 |

Example analysis of `0x40` (binary `01000000`):
- Bit 0: `0` = no encryption
- Bit 2: `0` = regular data updates
- Bits 5-7: `010` = BTHome Version 2

### Measurements

Measurements follow the device information byte, each containing:
- Object ID (1 byte) - specifies measurement type
- Data (1-4 bytes) - value in little-endian format
- Factor - multiplier to achieve proper scale

**Important ordering rule**: Object IDs must appear in numerical order (low to high) to ensure backward compatibility with older receivers.

## Supported Sensor Data Types

### Temperature Measurements

| Object ID | Format | Factor | Unit |
|-----------|--------|--------|------|
| `0x02` | sint16 (2 bytes) | 0.01 | °C |
| `0x45` | sint16 (2 bytes) | 0.1 | °C |
| `0x57` | sint8 (1 byte) | 1 | °C |
| `0x58` | sint8 (1 byte) | 0.35 | °C |

Example: `02C409` = 2500 × 0.01 = 25.00°C

### Humidity Measurements

| Object ID | Format | Factor | Unit |
|-----------|--------|--------|------|
| `0x03` | uint16 (2 bytes) | 0.01 | % |
| `0x2E` | uint8 (1 byte) | 1 | % |

Example: `03BF13` = 5055 × 0.01 = 50.55%

### Battery and Power

| Object ID | Format | Factor | Unit |
|-----------|--------|--------|------|
| `0x01` | uint8 (1 byte) | 1 | % |
| `0x0B` | uint24 (3 bytes) | 0.01 | W |
| `0x0C` | uint16 (2 bytes) | 0.001 | V |
| `0x43` | uint16 (2 bytes) | 0.001 | A |
| `0x5C` | sint32 (4 bytes) | 0.01 | W |
| `0x5D` | sint16 (2 bytes) | 0.001 | A |
| `0x4A` | uint16 (2 bytes) | 0.1 | V |

### Environmental Sensors

| Object ID | Property | Format | Factor | Unit |
|-----------|----------|--------|--------|------|
| `0x04` | pressure | uint24 (3 bytes) | 0.01 | hPa |
| `0x05` | illuminance | uint24 (3 bytes) | 0.01 | lx |
| `0x08` | dewpoint | sint16 (2 bytes) | 0.01 | °C |
| `0x0D` | pm2.5 | uint16 (2 bytes) | 1 | ug/m3 |
| `0x0E` | pm10 | uint16 (2 bytes) | 1 | ug/m3 |
| `0x12` | CO2 | uint16 (2 bytes) | 1 | ppm |
| `0x13` | TVOC | uint16 (2 bytes) | 1 | ug/m3 |
| `0x14` | moisture | uint16 (2 bytes) | 0.01 | % |
| `0x2F` | moisture | uint8 (1 byte) | 1 | % |
| `0x56` | conductivity | uint16 (2 bytes) | 1 | µS/cm |

### Motion and Acceleration

| Object ID | Property | Format | Factor | Unit |
|-----------|----------|--------|--------|------|
| `0x51` | acceleration | uint16 (2 bytes) | 0.001 | m/s² |
| `0x63` | acceleration (signed) | sint32 (4 bytes) | 0.000001 | m/s² |
| `0x52` | gyroscope | uint16 (2 bytes) | 0.001 | °/s |

### Volume and Mass

| Object ID | Property | Format | Factor | Unit |
|-----------|----------|--------|--------|------|
| `0x06` | mass (kg) | uint16 (2 bytes) | 0.01 | kg |
| `0x07` | mass (lb) | uint16 (2 bytes) | 0.01 | lb |
| `0x47` | volume | uint16 (2 bytes) | 0.1 | L |
| `0x48` | volume | uint16 (2 bytes) | 1 | mL |
| `0x49` | volume flow rate | uint16 (2 bytes) | 0.001 | m3/hr |
| `0x4E` | volume | uint32 (4 bytes) | 0.001 | L |
| `0x4F` | water | uint32 (4 bytes) | 0.001 | L |
| `0x55` | volume storage | uint32 (4 bytes) | 0.001 | L |

### Energy and Utilities

| Object ID | Property | Format | Factor | Unit |
|-----------|----------|--------|--------|------|
| `0x0A` | energy | uint24 (3 bytes) | 0.001 | kWh |
| `0x4B` | gas | uint24 (3 bytes) | 0.001 | m3 |
| `0x4C` | gas | uint32 (4 bytes) | 0.001 | m3 |
| `0x4D` | energy | uint32 (4 bytes) | 0.001 | kWh |

### Speed, Distance, and Rotation

| Object ID | Property | Format | Factor | Unit |
|-----------|----------|--------|--------|------|
| `0x3F` | rotation | sint16 (2 bytes) | 0.1 | ° |
| `0x40` | distance (mm) | uint16 (2 bytes) | 1 | mm |
| `0x41` | distance (m) | uint16 (2 bytes) | 0.1 | m |
| `0x44` | speed | uint16 (2 bytes) | 0.01 | m/s |
| `0x5E` | direction | uint16 (2 bytes) | 0.01 | ° |
| `0x5F` | precipitation | uint16 (2 bytes) | 0.1 | mm |
| `0x61` | rotational speed | uint16 (2 bytes) | 1 | rpm |
| `0x62` | speed (signed) | sint32 (4 bytes) | 0.000001 | m/s |

### Counters

| Object ID | Format | Factor | Unit |
|-----------|--------|--------|------|
| `0x09` | uint8 (1 byte) | 1 | — |
| `0x3D` | uint16 (2 bytes) | 1 | — |
| `0x3E` | uint32 (4 bytes) | 1 | — |
| `0x59` | sint8 (1 byte) | 1 | — |
| `0x5A` | sint16 (2 bytes) | 1 | — |
| `0x5B` | sint32 (4 bytes) | 1 | — |

### Special Types

#### Timestamp (`0x50`)

Unix epoch time (seconds since 1970-01-01 00:00:00 UTC) as uint32 (4 bytes). Example: `0x5D396164` = 1684093277 seconds = 2023-05-14 19:41:17 UTC

#### Text (`0x53`)

Variable length UTF-8 encoded text. Format: Object ID + length byte + text data. Example: `0x530C48656C6C6F20576F726C6421` = "Hello World!" (12 bytes)

#### Raw (`0x54`)

Variable length raw binary data. Format: Object ID + length byte + hex data. Reported as hexadecimal string.

#### Light Level (`0x64`)

uint8 with discrete values: 0 = dark, 1 = twilight, 2 = bright

#### Channel (`0x60`)

uint8 (1 byte), factor 1

#### Settings Revision (`0x65`)

uint8 (1 byte), factor 1

### Duration

| Object ID | Format | Factor | Unit |
|-----------|--------|--------|------|
| `0x42` | uint24 (3 bytes) | 0.001 | s |

### UV Index

| Object ID | Format | Factor | Unit |
|-----------|--------|--------|------|
| `0x46` | uint8 (1 byte) | 0.1 | — |

### Multiple Measurements

Multiple measurements of the same type can be included in a single advertisement. Each additional measurement of the same type receives a numeric suffix (temperature_2, temperature_3, etc.). Maintain consistent ordering across advertisements to prevent incorrect assignment.

## Binary Sensor Data

Binary sensors transmit uint8 values: `0` = off/false, `1` = on/true

| Object ID | Property | Meaning (0/1) |
|-----------|----------|---------------|
| `0x0F` | generic boolean | Off / On |
| `0x10` | power | Off / On |
| `0x11` | opening | Closed / Open |
| `0x15` | battery | Normal / Low |
| `0x16` | battery charging | Not Charging / Charging |
| `0x17` | carbon monoxide | Not detected / Detected |
| `0x18` | cold | Normal / Cold |
| `0x19` | connectivity | Disconnected / Connected |
| `0x1A` | door | Closed / Open |
| `0x1B` | garage door | Closed / Open |
| `0x1C` | gas | Clear / Detected |
| `0x1D` | heat | Normal / Hot |
| `0x1E` | light | No light / Light detected |
| `0x1F` | lock | Locked / Unlocked |
| `0x20` | moisture | Dry / Wet |
| `0x21` | motion | Clear / Detected |
| `0x22` | moving | Not moving / Moving |
| `0x23` | occupancy | Clear / Detected |
| `0x24` | plug | Unplugged / Plugged in |
| `0x25` | presence | Away / Home |
| `0x26` | problem | OK / Problem |
| `0x27` | running | Not Running / Running |
| `0x28` | safety | Unsafe / Safe |
| `0x29` | smoke | Clear / Detected |
| `0x2A` | sound | Clear / Detected |
| `0x2B` | tamper | Off / On |
| `0x2C` | vibration | Clear / Detected |
| `0x2D` | window | Closed / Open |

## Events

Devices can transmit events representing user actions or state changes. Event support is available in Home Assistant 2023.5 and higher.

### Button Events (`0x3A`)

| Event ID | Event Type |
|----------|------------|
| `0x00` | None |
| `0x01` | press |
| `0x02` | double_press |
| `0x03` | triple_press |
| `0x04` | long_press |
| `0x05` | long_double_press |
| `0x06` | long_triple_press |
| `0x80` | hold_press |

Examples: `3A00` = no event, `3A01` = press, `3A04` = long_press

### Command Events (`0x3B`)

| Event ID | Type | Parameter |
|----------|------|-----------|
| `0x00` | off | — |
| `0x01` | on | — |
| `0x02` | toggle | — |
| `0x03` | step up | number of steps |
| `0x04` | step down | number of steps |

Format: Object ID + argument length byte + opcode byte + argument bytes

Example: `0x3B010305` = step up 5 steps
- `0x3B` = command object
- `0x01` = 1 byte argument length
- `0x03` = opcode (step up)
- `0x05` = 5 steps

Commands should be encrypted to prevent unauthorized observation or spoofing.

### Dimmer Events (`0x3C`)

| Event ID | Type | Parameter |
|----------|------|-----------|
| `0x00` | None | — |
| `0x01` | rotate left | number of steps |
| `0x02` | rotate right | number of steps |

Examples: `3C0103` = rotate left 3 steps, `3C020A` = rotate right 10 steps

### Multiple Events

Multiple events of the same type can be transmitted by concatenating them. The `0x00` (None) event is useful for multi-button devices when reporting only specific button presses.

Example: `3A003A01` = no event for first button, press event for second button

## Device Information

Optional fields for device identification and management:

| Object ID | Property | Format | Example | Result |
|-----------|----------|--------|---------|--------|
| `0xF0` | device type id | uint16 (2 bytes) | `F00100` | 1 |
| `0xF1` | firmware version | uint32 (4 bytes) | `F100010204` | 4.2.1.0 |
| `0xF2` | firmware version | uint24 (3 bytes) | `F2000106` | 6.1.0 |

Device type IDs distinguish between different device models. Firmware versions support two formats: `0.0.0.1` (32-bit) or `0.0.1` (24-bit).

## Miscellaneous Data

### Packet ID (`0x00`)

Optional uint8 (1 byte) ranging from 0-255. Increments with each data change to filter duplicate advertisements. Receivers should only process packets with different IDs than the previous advertisement. Many home automation systems already filter unchanged data, making this optional.

Example: `0009` = packet ID 9

## Encryption

BTHome supports AES encryption in CCM mode using a pre-shared key for security-sensitive data. Unencrypted advertisements can be read by any nearby Bluetooth listener.

### Key Requirements

- 16 bytes (32 hexadecimal characters) long
- Pre-shared between sender and receiver
- Enables encrypted data to remain unreadable without the key

### Implementation Guidance

When the encryption flag (bit 0 in device information byte) is set to `1`, data is encrypted. Detailed encryption specifications are available on the BTHome encryption documentation page.

## Example Payload Analysis

Complete example: `020106 0B094449592D73656E736F72 0A16D2FC4002C40903BF13`

### Flags Element
`020106`
- Length: 2, Type: Flags (`0x01`), Value: `06` (LE General Discoverable Mode + BR/EDR Not Supported)

### Local Name Element
`0B094449592D73656E736F72`
- Length: 11, Type: Complete Local Name (`0x09`), Name: "DIY-sensor"

### Service Data Element
`0A16D2FC4002C40903BF13`
- Length: 10, Type: Service Data - 16-bit UUID (`0x16`)
- Data: `D2FC4002C40903BF13`

#### BTHome Data Breakdown
- UUID: `D2FC` (reversed = `0xFCD2`)
- Device Info: `40` (unencrypted, regular intervals, version 2)
- Temperature: `02C409` = 25.00°C
- Humidity: `03BF13` = 50.55%

## Standards and References

- BLE packet format specifications available from Bluetooth SIG
- BTHome UUID sponsored by Allterco Robotics (Shelly)
- Standardized AD types from Generic Access Profile specifications
- Full example payloads for each data type available on GitHub

## Credits

BTHome is created by Ernst Klamer with contributions from Victor and Paulus Schoutsen, sponsored by Shelly.

---

## Relevant fields for this project (freezer temp monitor)

- Temperature: object ID `0x02`, sint16, factor 0.01, °C — best resolution for a freezer (range well within sint16, e.g. -20.00°C = -2000 = 0xF830)
- Battery: object ID `0x01`, uint8, factor 1, % — for low-battery alerting (see project failure-alerting notes)
- Packet ID: object ID `0x00`, uint8 — optional but cheap, useful for diagnosing missed/duplicate advertisements
- Object IDs must be ascending: `0x00` (packet id) < `0x01` (battery) < `0x02` (temperature) — so payload order should be packet id, battery, then temperature
