/*
 * Freezer Monitor - nRF52840 + DS18B20 + BTHome v2 over BLE
 *
 * Board: Teyleten Pro Micro nRF52840 (nice!nano v2 clone)
 *   - Arduino core: Adafruit nRF52 + Community Add-on (nice!nano-family board)
 *   - Pin notes: docs/hardware/teyleten-nrf52840-promicro.md
 *
 * Cycle: wake -> read DS18B20 -> read battery -> advertise BTHome v2 packet
 *        -> sleep -> repeat
 *
 * BTHome v2 reference: docs/bthome/format-v2.md
 */

#include <bluefruit.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// ---------------------------------------------------------------------------
// Pin configuration
// P0.xx = Arduino pin xx (0-31); P1.xx = Arduino pin (32 + xx) - confirmed via
// the nice_nano variant.h. Avoid P0.14 / P0.16 (reported problematic, UNVERIFIED)
// and P0.18/P0.19 (RESET / no connection per variant.h).
// ---------------------------------------------------------------------------
#define ONEWIRE_PIN     24  // P0.24 (left side, position 5) - DS18B20 data line (needs 4.7k pull-up to 3V3)

// Battery voltage divider: two 1M resistors in series from B+ to GND, midpoint
// to P0.02/A0 (right side, position 6). CONFIRMED 2026-06-15 that PIN_VBAT
// (P0.31) and A2 (P0.04) are floating/unusable on this clone - this external
// divider replaces that approach.
#define BATT_ADC_PIN    A0  // P0.02

// Empirical scale factor: B+ measured at 3.56V via multimeter while
// analogRead(BATT_ADC_PIN) averaged ~8030 (range 7984-8076). BATT_SCALE =
// 3.56 / 8030. Good enough given the LS14250's flat discharge curve - we're
// mainly looking for the late-life voltage cliff, not precise %.
#define BATT_SCALE      0.0004434f

// LS14250 (Li-SOCl2) discharge curve is flat near its 3.6V nominal voltage for
// most of its life, then drops sharply near end-of-life. A linear map between
// these two points will read near 100% for most of the cell's life and fall
// quickly once the cliff is reached - which is the useful signal for failure
// alerting (see CLAUDE.md / docs/hardware notes).
#define BATT_FULL_V     3.6f   // nominal fresh-cell voltage -> 100%
#define BATT_EMPTY_V    2.0f   // datasheet end-of-discharge voltage -> 0%

// ---------------------------------------------------------------------------
// Timing
// ---------------------------------------------------------------------------
#define SLEEP_INTERVAL_MS     (5UL * 60UL * 1000UL)   // 5 minutes
#define ADVERTISE_DURATION_MS 2000                   // how long to advertise each cycle

// ---------------------------------------------------------------------------
// BTHome v2 (see docs/bthome/format-v2.md)
// Object IDs must stay in ascending order: packet id (0x00) < battery (0x01)
// < temperature (0x02).
// ---------------------------------------------------------------------------
#define BTHOME_UUID16_LO      0xD2   // 0xFCD2, little-endian
#define BTHOME_UUID16_HI      0xFC
#define BTHOME_DEVICE_INFO    0x40   // unencrypted, regular interval, version 2

#define BTHOME_ID_PACKET_ID   0x00
#define BTHOME_ID_BATTERY     0x01
#define BTHOME_ID_TEMPERATURE 0x02


OneWire oneWire(ONEWIRE_PIN);
DallasTemperature sensors(&oneWire);

uint8_t packetId = 0;

void setup() {
  analogReadResolution(14);

  sensors.begin();

  // First conversion right after begin() reliably reads -127
  // (DEVICE_DISCONNECTED_C) on this sensor - throw away one reading here so
  // loop()'s first real reading is valid.
  sensors.requestTemperatures();
  sensors.getTempCByIndex(0);

  Bluefruit.begin();
  Bluefruit.setName("FreezerMonitor");
  Bluefruit.setTxPower(8);  // nRF52840 max; helps punch through freezer lid attenuation
  pinMode(38, OUTPUT);     // P1.06 = 32 + 6, per your variant map
  digitalWrite(38, HIGH);
}

void loop() {
  float tempC = readTemperatureC();
  float battV = readBatteryVoltage();
  uint8_t batteryPct = readBatteryPercent(battV);

  sendBTHomeAdvertisement(tempC, batteryPct);
  delay(ADVERTISE_DURATION_MS);
  Bluefruit.Advertising.stop();

  delay(SLEEP_INTERVAL_MS);
}

// Returns DallasTemperature's DEVICE_DISCONNECTED_C (-127.0) if the DS18B20
// can't be read. That gets encoded into the BTHome payload as-is (an obviously
// out-of-range freezer temperature) rather than silently sending a stale or
// fabricated value - see project notes on failure alerting.
float readTemperatureC() {
  sensors.requestTemperatures();
  return sensors.getTempCByIndex(0);
}

// Averages a few samples from the external divider on BATT_ADC_PIN to smooth
// out the ~1% ADC noise observed during calibration.
float readBatteryVoltage() {
  const int numSamples = 8;
  uint32_t total = 0;
  for (int i = 0; i < numSamples; i++) {
    total += analogRead(BATT_ADC_PIN);
    delay(2);
  }
  float avgRaw = (float)total / numSamples;
  return avgRaw * BATT_SCALE;
}

uint8_t readBatteryPercent(float battV) {
  float pct = (battV - BATT_EMPTY_V) / (BATT_FULL_V - BATT_EMPTY_V) * 100.0f;
  if (pct > 100.0f) pct = 100.0f;
  if (pct < 0.0f) pct = 0.0f;
  return (uint8_t)round(pct);
}

void sendBTHomeAdvertisement(float tempC, uint8_t batteryPct) {
  int16_t tempRaw = (int16_t)round(tempC * 100.0f);

  uint8_t payload[] = {
    BTHOME_UUID16_LO, BTHOME_UUID16_HI,
    BTHOME_DEVICE_INFO,
    BTHOME_ID_PACKET_ID, packetId++,
    BTHOME_ID_BATTERY, batteryPct,
    BTHOME_ID_TEMPERATURE, (uint8_t)(tempRaw & 0xFF), (uint8_t)((tempRaw >> 8) & 0xFF),
  };

  Bluefruit.Advertising.clearData();
  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addData(BLE_GAP_AD_TYPE_SERVICE_DATA, payload, sizeof(payload));

  // Interval units are 0.625ms; 160 = 100ms.
  Bluefruit.Advertising.setInterval(160, 160);
  Bluefruit.Advertising.start(0); // 0 = no timeout; stopped manually after ADVERTISE_DURATION_MS
}
