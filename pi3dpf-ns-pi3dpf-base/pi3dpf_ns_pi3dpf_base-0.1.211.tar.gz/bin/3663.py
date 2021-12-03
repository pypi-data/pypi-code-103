#!/usr/bin/env python3
# From: http://raspberrypiguide.de/howtos/raspberry-pi-gpio-how-to/

import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)

GPIO.setup(16, GPIO.OUT)
GPIO.output(16, GPIO.HIGH)
time.sleep(0.5)
GPIO.output(16, GPIO.LOW)
