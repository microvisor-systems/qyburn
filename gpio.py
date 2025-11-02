from gpiozero import LED
from time import sleep

red_led = LED(6)
green_led = LED(26)
blue_led = LED(17)
yellow_led = LED(21)
white_led = LED(12)

while True:
    red_led.on()
    green_led.on()
    blue_led.on()
    yellow_led.on()
    white_led.on()
    sleep(1)
    red_led.off()
    green_led.off()
    blue_led.off()
    yellow_led.off()
    white_led.off()
    sleep(1)
