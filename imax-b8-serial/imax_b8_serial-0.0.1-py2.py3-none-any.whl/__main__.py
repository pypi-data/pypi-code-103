#! /usr/bin/env python3
"""Serial interface to monitor LiPo charger."""

import argparse

import serial  # type: ignore

from . import read


def main() -> None:  # pragma: no cover
    """Entrypoint."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("serial", help="Serial port device")
    args = parser.parse_args()
    for packet in read(serial.Serial(port=args.serial, baudrate=9600)):
        for attr in dir(packet):
            if not attr.startswith("_"):
                print(attr, "=", packet[attr])


if __name__ == "__main__":  # pragma: no cover
    main()
