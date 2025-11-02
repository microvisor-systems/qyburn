from gpiozero import LED
from time import sleep

# This works on ALL Raspberry Pi models including Pi 5!
led = LED(17)

try:
    while True:
        led.on()
        print("LED ON")
        sleep(1)

        led.off()
        print("LED OFF")
        sleep(1)

except KeyboardInterrupt:
    print("\nStopped!")
    led.close()
