from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory

Device.pin_factory = LGPIOFactory()

from gpiozero import Servo
from time import sleep

SERVO_PIN = 25


# Create servo
servo = Servo(SERVO_PIN, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000)

try:
    # STOP (center position)
    print("STOP")
    servo.value = 0  # Center = STOP
    sleep(2)

    # Rotate CLOCKWISE slowly
    print("Clockwise - Slow")
    servo.value = 0.3  # Positive = clockwise
    sleep(3)

    # STOP
    print("STOP")
    servo.value = 0
    sleep(2)

    # Rotate CLOCKWISE fast
    print("Clockwise - Fast")
    servo.value = 1.0  # Max speed clockwise
    sleep(3)

    # STOP
    print("STOP")
    servo.value = 0
    sleep(2)

    # Rotate COUNTER-CLOCKWISE slowly
    print("Counter-clockwise - Slow")
    servo.value = -0.3  # Negative = counter-clockwise
    sleep(3)

    # STOP
    print("STOP")
    servo.value = 0
    sleep(2)

    # Rotate COUNTER-CLOCKWISE fast
    print("Counter-clockwise - Fast")
    servo.value = -1.0  # Max speed counter-clockwise
    sleep(3)

    # STOP
    print("STOP")
    servo.value = 0

    print("\n✓ Test complete!")

except KeyboardInterrupt:
    print("\n\nStopped!")

finally:
    servo.value = 0  # STOP
    sleep(0.3)
    servo.close()
    print("Servo stopped and released")
