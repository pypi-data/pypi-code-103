#!/usr/bin/env python3
"""
Rotate display and devices based accelerometer data.
Usage:
    # rotate devices/display upside down
    Accelrotate().rotate('inverted')

Inspired by:
https://gist.githubusercontent.com/ei-grad/4d9d23b1463a99d24a8d/raw/rotate.py
https://github.com/ffejery/thinkpad-l380-yoga-scripts
https://github.com/admiralakber/thinkpad-yoga-scripts

"""
import sys
import click
import re

from pathlib import Path
from shutil import ReadError
from time import sleep
from subprocess import check_call, check_output
from glob import glob
from typing import Literal, Pattern, Union


# CONSTANTS
GRAVITY = 7.0  # (m^2 / s) sensibility, gravity trigger

RotationNames = Literal["normal", "inverted", "left", "right"]


class Accelrotate:
    ROTATIONS = {
        "normal": {
            "pen": "none",
            "coord": "1 0 0 0 1 0 0 0 1",
            "check": lambda x, y: y <= -GRAVITY,
        },
        "inverted": {
            "pen": "half",
            "coord": "-1 0 1 0 -1 1 0 0 1",
            "check": lambda x, y: y >= GRAVITY,
        },
        "left": {
            "pen": "ccw",
            "coord": "0 -1 1 1 0 0 0 0 1",
            "check": lambda x, y: x >= GRAVITY,
        },
        "right": {
            "pen": "cw",
            "coord": "0 1 0 -1 0 1 0 0 1",
            "check": lambda x, y: x <= -GRAVITY,
        },
    }

    def __init__(
        self,
        rotate_wacom_devices: Union[str, Pattern] = "wacom",
        rotate_xdevices: Union[str, Pattern] = "touchscreen|touch digitizer|trackpoint",
        rotate_display: bool = True,
    ):
        """
        Manager for X device rotation based on accelerometer device

        Parameters
        ----------
        wacom_names : Union[str, Pattern], optional
            pattern for wacom device rotation (via xsetwacom), by default "wacom"
        xdevices : Union[ str, Pattern ], optional
            pattern for X device roation (via xinput), by default "touchscreen|touch digitizer|finger touch|touchpad|trackpoint"

        Raises
        ------
        ReadError
            raised when accelerator devices could not be found
        """
        # find which system bus device is accelerator device
        for device in glob("/sys/bus/iio/devices/iio:device*/name"):
            with open(device) as f:
                if "accel" in f.read():
                    self.basedir = Path(device.rsplit("/name", 1)[0])
                    break
        else:
            raise ReadError("cannot find any accelerator devices")
        self._in_accel_x_raw = None
        self._in_accel_y_raw = None
        self._in_accel_scale = None

        _devices_all = (
            check_output(["xinput", "--list", "--name-only"]).decode().split("\n")
        )
        self.rotate_xdevices = (
            [name for name in _devices_all if re.search(rotate_xdevices, name, re.I)]
            if rotate_xdevices
            else []
        )
        self.rotate_wacom_devices = (
            [
                name
                for name in _devices_all
                if re.search(rotate_wacom_devices, name, re.I)
            ]
            if rotate_wacom_devices
            else []
        )
        self.rotate_display = rotate_display

    @property
    def x(self):
        """get current scaled X coordinates"""
        if self._in_accel_x_raw is None:
            self._in_accel_x_raw = open(self.basedir / "in_accel_x_raw")
        self._in_accel_x_raw.seek(0)
        return float(self._in_accel_x_raw.read())

    @property
    def x_scaled(self):
        """get scalled X coordinates"""
        return self.x * self.scale

    @property
    def y(self):
        """get current scaled Y coordinates"""
        if self._in_accel_y_raw is None:
            self._in_accel_y_raw = open(self.basedir / "in_accel_y_raw")
        self._in_accel_y_raw.seek(0)
        return float(self._in_accel_y_raw.read())

    @property
    def y_scaled(self):
        """get scalled Y coordinates"""
        return self.y * self.scale

    @property
    def scale(self):
        """get current scale"""
        if self._in_accel_scale is None:
            self._in_accel_scale = open(self.basedir / "in_accel_scale")
        self._in_accel_scale.seek(0)
        return float(self._in_accel_scale.read())

    def rotate_display_server(self, rotation: RotationNames):
        """rotate X display to a specific rotation"""
        check_call(["xrandr", "-o", rotation])

    def rotate(self, rotation: Literal["normal", "inverted", "left", "right"]):
        """rotate entire device (touchpad, touchscreen, display, pen) to a specific rotation"""
        rotation_conf = self.ROTATIONS[rotation]
        # rotate display
        if self.rotate_display:
            print(f"rotating DISPLAY to {rotation}")
            self.rotate_display_server(rotation)
        # rotate X devices
        for dev in self.rotate_xdevices:
            print(f'rotating "{dev}" to {rotation}')
            check_call(
                [
                    "xinput",
                    "set-prop",
                    dev,
                    "Coordinate Transformation Matrix",
                ]
                + rotation_conf["coord"].split(),
            )
        # rotate wacom devices
        for dev in self.rotate_wacom_devices:
            print(f'rotating "{dev}" to {rotation}')
            check_call(["xsetwacom", "set", dev, "rotate", rotation_conf["pen"]])

    def rotation_loop(self, sleep_time=0.1):
        """keep checking device rotation and apply matching states"""
        current_state = None
        while True:
            for name, state_conf in self.ROTATIONS.items():
                if name != current_state:
                    if state_conf["check"](self.x_scaled, self.y_scaled):
                        current_state = name
                        self.rotate(name)
                        break
            sleep(sleep_time)


@click.command()
@click.argument(
    "rotation",
    required=False,
    type=click.Choice(["normal", "inverted", "left", "right"]),
)
@click.option("--no-display", "-d", is_flag=True, help="do not rotate display")
@click.option(
    "--loop",
    "-l",
    is_flag=True,
    help="continuesly check rotation in loop every X second where",
)
@click.option(
    "--wacom",
    "-w",
    help="rotate wacom devices that match name pattern",
    default="wacom",
    show_default=True,
)
@click.option(
    "--xorg",
    "-x",
    help="rotate Xorg devices that match name pattern",
    default="touchscreen|touch digitizer|trackpoint",
    show_default=True,
)
def cli(loop: float, wacom: str, xorg: str, no_display: bool, rotation: str):
    """Rotate display and devices based on accelerometer data"""
    acc = Accelrotate(
        rotate_wacom_devices=wacom,
        rotate_xdevices=xorg,
        rotate_display=not no_display,
    )
    if loop:
        acc.rotation_loop()
    elif rotation:
        acc.rotate(rotation)
    else:
        print("either rotation argument or --loop flag needs to provided")
        sys.exit(1)
    sys.exit()


if __name__ == "__main__":
    cli()
