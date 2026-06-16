# Firmware

Arduino sketch for the nRF52840 (Adafruit nRF52 BSP).

Responsibilities:
- Read temperature from the DS18B20 (OneWire / DallasTemperature)
- Read battery voltage/level
- Assemble and send a BTHome v2 BLE advertisement
- Sleep between readings to conserve the 14250 cell

Not yet implemented.
