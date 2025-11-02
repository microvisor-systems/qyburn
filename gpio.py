#!/usr/bin/env python3
"""
LED Control using gpiod for Raspberry Pi 5
Clean, modern GPIO interface
"""

import gpiod
import time

# Configuration
CHIP_NAME = "gpiochip0"  # Pi 5 uses gpiochip4
LED_PIN = 26  # GPIO 26

# Open GPIO chip
chip = gpiod.Chip(CHIP_NAME)

# Request the GPIO line (pin) as output
led_line = chip.get_line(LED_PIN)
led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)

print(f"✓ LED initialized on GPIO {LED_PIN} using gpiod")

try:
    while True:
        # LED ON
        led_line.set_value(1)
        print("LED ON")
        time.sleep(1)

        # LED OFF
        led_line.set_value(0)
        print("LED OFF")
        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopped by user")

finally:
    # Clean up
    led_line.set_value(0)  # Turn off
    led_line.release()
    chip.close()
    print("Cleaned up GPIO")
