from Adafruit_BBIO import GPIO
from Adafruit_BBIO.GPIO import HIGH, LOW


def setup_output(pin: str):
    """Set up a GPIO as output."""

    GPIO.setup(pin, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)


def setup_input(pin: str, pull_mode: str = "UP"):
    """Set up a GPIO as input."""
    GPIO.setup(pin, GPIO.IN, GPIO.PUD_DOWN if pull_mode == "DOWN" else GPIO.PUD_UP)


def write_output(pin: str, value: str):
    """Write a value to a GPIO."""

    GPIO.output(pin, value)


def read_input(pin: str, on_state=LOW):
    """Read a value from a GPIO."""
    return GPIO.input(pin) is on_state


def edge_detect(pin, callback, bounce):
    """Add detection for RISING and FALLING events."""

    GPIO.add_event_detect(pin, GPIO.FALLING, callback=callback, bouncetime=bounce)
