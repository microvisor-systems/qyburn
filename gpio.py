from gpiozero import LED
from time import sleep

green_led = LED(26)
blue_led = LED(17)
yellow_led = LED(21)

while True:
    green_led.on()
    blue_led.on()
    yellow_led.on()
    sleep(1)
    green_led.on()
    blue_led.on()
    yellow_led.off()
    sleep(1)
