#!/usr/bin/env python3
import curses
from time import sleep
import RPi.GPIO as GPIO

RED, GREEN, BLUE, YELLOW = 4, 26, 17, 2
FREQ = 1000
STEP = 2


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for pin in (RED, GREEN, BLUE, YELLOW):
        GPIO.setup(pin, GPIO.OUT)
    p_red = GPIO.PWM(RED, FREQ)
    p_green = GPIO.PWM(GREEN, FREQ)
    p_blue = GPIO.PWM(BLUE, FREQ)
    p_yellow = GPIO.PWM(YELLOW, FREQ)
    p_red.start(0)
    p_green.start(0)
    p_blue.start(0)
    p_yellow.start(0)
    return p_red, p_green, p_blue, p_yellow


def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))


def run(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    p_red, p_green, p_blue, p_yellow = setup()
    brightness = {"red": 0, "green": 0, "blue": 0, "yellow": 0}
    selected = "red"  # Start controlling the red LED

    def apply_brightness():
        p_red.ChangeDutyCycle(brightness["red"])
        p_green.ChangeDutyCycle(brightness["green"])
        p_blue.ChangeDutyCycle(brightness["blue"])
        p_yellow.ChangeDutyCycle(brightness["yellow"])

    try:
        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, f"Controlling: {selected} | Brightness: {brightness[selected]:3d}%")
            stdscr.addstr(2, 0, "↑/↓: Adjust brightness   ←/→: Select LED   Q: quit")
            stdscr.addstr(3, 0, "LEDs: RED, GREEN, BLUE, YELLOW")
            stdscr.refresh()

            ch = stdscr.getch()

            if ch in (ord('q'), ord('Q')):
                break
            elif ch == curses.KEY_LEFT:
                # Select previous LED
                order = ["red", "green", "blue", "yellow"]
                idx = order.index(selected) - 1
                selected = order[idx]
            elif ch == curses.KEY_RIGHT:
                # Select next LED
                order = ["red", "green", "blue", "yellow"]
                idx = (order.index(selected) + 1) % 4
                selected = order[idx]
            elif ch == curses.KEY_UP:
                brightness[selected] = clamp(brightness[selected] + STEP)
                apply_brightness()
            elif ch == curses.KEY_DOWN:
                brightness[selected] = clamp(brightness[selected] - STEP)
                apply_brightness()

            sleep(0.01)
    finally:
        for pin in (p_red, p_green, p_blue, p_yellow):
            pin.ChangeDutyCycle(0)
            pin.stop()
        GPIO.cleanup()


if __name__ == "__main__":
    curses.wrapper(run)
