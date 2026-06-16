/*
 * Board Bring-up - P0.13 rail-switch + identity test
 * Teyleten Pro Micro nRF52840 (nice!nano v2 clone)
 *
 * Runs entirely on battery (B+/B-) - no USB, no serial monitor needed.
 * LED (PIN_LED1 / onboard blue LED) signals which phase is active.
 *
 * Loops forever:
 *   Phase 1 - P0.13 LOW, LED OFF, 10s
 *     -> multimeter: red lead on VCC (right side, pos 9), black on any GND
 *   Phase 2 - P0.13 HIGH, LED ON, 10s
 *     -> multimeter: read VCC again, compare to phase 1
 *     (these two phases tell us P0.13's rail-switch polarity, if any)
 *   Phase 3 - P0.13 held LOW, LED rapid-flashing, 30s
 *     -> multimeter: red lead on right side positions 3, 4, 5 in turn
 *        (black on any GND) - whichever reads ~0V is the pin physically
 *        wired to P0.13. The other two are SPI pins (P1.11/P1.13) and
 *        should float/read unstable.
 *
 * CONFIRMED 2026-06-15: P0.14 and P0.16 hang/crash-loop the board as soon as
 * either is configured as GPIO - neither is used here.
 */

#include <Arduino.h>

#define SENSOR_PWR_PIN 13

void setup() {
  pinMode(SENSOR_PWR_PIN, OUTPUT);
  pinMode(PIN_LED1, OUTPUT);
}

void loop() {
  // Phase 1: P0.13 LOW, LED off - read VCC
  digitalWrite(SENSOR_PWR_PIN, LOW);
  digitalWrite(PIN_LED1, !LED_STATE_ON);
  delay(10000);

  // Phase 2: P0.13 HIGH, LED on - read VCC again
  digitalWrite(SENSOR_PWR_PIN, HIGH);
  digitalWrite(PIN_LED1, LED_STATE_ON);
  delay(10000);

  // Phase 3: P0.13 held LOW, LED rapid-flash - identify which physical pin
  // (right side 3, 4, or 5) is actually P0.13
  digitalWrite(SENSOR_PWR_PIN, LOW);
  uint32_t phaseStart = millis();
  while (millis() - phaseStart < 30000) {
    digitalWrite(PIN_LED1, LED_STATE_ON);
    delay(100);
    digitalWrite(PIN_LED1, !LED_STATE_ON);
    delay(100);
  }

  // Reboot - starts the whole cycle over from a clean reset
  NVIC_SystemReset();
}
