from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory

Device.pin_factory = LGPIOFactory()

from gpiozero import Servo
from time import sleep

# Change this to your GPIO pin
servo = Servo(2, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000)

try:
    while True:
        servo.min()  # 0 degrees
        sleep(1)
        servo.mid()  # 90 degrees
        sleep(1)
        servo.max()  # 180 degrees
        sleep(1)
except KeyboardInterrupt:
    servo.mid()
    servo.close()
