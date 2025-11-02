from gpiozero import LED
from time import sleep

# LED pins
RED_LED_PIN = 6
GREEN_LED_PIN = 26
BLUE_LED_PIN = 17
YELLOW_LED_PIN = 21
WHITE_LED_PIN = 12

class FirmwareController:
    """Controls LEDs for quantum music concert"""

    def __init__(self):
        # Initialize LEDs
        self.red_led = LED(RED_LED_PIN)
        self.green_led = LED(GREEN_LED_PIN)
        self.blue_led = LED(BLUE_LED_PIN)
        self.yellow_led = LED(YELLOW_LED_PIN)
        self.white_led = LED(WHITE_LED_PIN)

        # LED list for easy access
        self.leds = [self.red_led, self.green_led, self.blue_led, self.yellow_led, self.white_led]

    def blink_leds(self, duration=1.0):
        """Blink all LEDs on and off"""
        # Turn all on
        for led in self.leds:
            led.on()
        sleep(duration)

        # Turn all off
        for led in self.leds:
            led.off()
        sleep(duration)

    def set_led_brightness(self, led_index, brightness):
        """Set LED brightness (0-1)"""
        if 0 <= led_index < len(self.leds):
            if brightness > 0.5:
                self.leds[led_index].on()
            else:
                self.leds[led_index].off()

    def sync_to_numbers(self, numbers, duration=0.3):
        """Sync LEDs to quantum-generated numbers"""
        for num in numbers:
            # Map number to LED pattern (simple on/off based on number mod 5)
            led_pattern = num % 5
            for i, led in enumerate(self.leds):
                if i == led_pattern:
                    led.on()
                else:
                    led.off()

            sleep(duration)

        # Turn off LEDs at end
        for led in self.leds:
            led.off()

    def cleanup(self):
        """Clean up GPIO resources"""
        for led in self.leds:
            led.off()


# Simple demo functions

def demo_leds():
    """Demo LED blinking"""
    controller = FirmwareController()
    try:
        while True:
            controller.blink_leds(1.0)
    except KeyboardInterrupt:
        print("Stopping LEDs...")
    finally:
        controller.cleanup()


if __name__ == "__main__":
    # Run LED demo
    print("Running LED demo...")
    demo_leds()