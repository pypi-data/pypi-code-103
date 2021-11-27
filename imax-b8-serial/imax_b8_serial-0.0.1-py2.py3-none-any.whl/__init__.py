"""Serial interface to monitor LiPo charger."""

from ctypes import Structure, c_ubyte, c_uint16, c_ushort
from typing import Any, Iterator

import serial  # type: ignore


class Settings(Structure):
    """Settings."""

    _pack_ = 1
    _fields_ = [
        ("Temp Cutoff", c_ubyte, 1),
        ("a", c_ubyte, 1),
        ("Capacity Cutoff", c_ubyte, 1),
        ("Key beep", c_ubyte, 1),
        ("Buzz", c_ubyte, 1),
        ("c", c_ubyte, 1),
        ("d", c_ubyte, 1),
        ("e", c_ubyte, 1),
    ]

    def __getitem__(self, attr: str) -> Any:
        """Decode the settings into pythonic."""
        return self.__getattribute__(attr)


class Packet(Structure):
    """Communication packet."""

    _fields_ = [
        ("settings", Settings),
        ("nimh_sensitivity", c_ubyte),
        ("nicd_sensitivity", c_ubyte),
        ("temp_cutoff", c_ubyte),
        ("waste_time", c_ubyte),
        ("backlight", c_ubyte),
        ("input_cuttoff", c_ubyte),
        ("mode", c_ubyte),
        ("nicd_charge_current", c_ubyte),
        ("nicd_discharge_current", c_ubyte),
        ("nicd_cycle", c_ubyte),
        ("nicd_cycles", c_ubyte),
        ("nimh_charge_current", c_ubyte),
        ("nimh_discharge_current", c_ubyte),
        ("nimh_cycle", c_ubyte),
        ("nimh_cycles", c_ubyte),
        ("lipo_charge_current", c_ubyte),
        ("lipo_cells", c_ubyte),
        ("lipo_discharge_current", c_ubyte),
        ("_a", c_ubyte),
        ("pb_charge_current", c_ubyte),
        ("pb_cells", c_ubyte),
        ("type", c_ubyte),
        ("active", c_ubyte),
        ("nimh_dischage_cutoff", c_uint16),
        ("nicd_discharge_cutoff", c_uint16),
        ("_b", c_ubyte),
        ("safty_timer", c_ubyte),
        ("capacity_cuttoff", c_uint16),
        ("current", c_uint16),
        ("voltage", c_uint16),
        ("temp_external", c_uint16),
        ("temp_internal", c_uint16),
        ("input_voltage", c_uint16),
        ("charge", c_uint16),
        ("lipo_cell0", c_uint16),
        ("lipo_cell1", c_uint16),
        ("lipo_cell2", c_uint16),
        ("lipo_cell3", c_uint16),
        ("lipo_cell4", c_uint16),
        ("lipo_cell5", c_uint16),
        ("lipo_cell6", c_uint16),
        ("lipo_cell7", c_uint16),
    ]

    def __getitem__(self, attr: str) -> Any:
        """Decode the packet into pythonic."""
        val = self.__getattribute__(attr)
        if dict(self._fields_)[attr] == c_ushort:
            val = (val >> 8) / 100.0 + (val & 0xFF)
        if attr == "backlight":
            val = "%d%%" % (val * 5)
        if attr == "mode":
            val = {0: "Discharge", 1: "Charge", 0x10: "D to C", 0x11: "C to D"}[val]
        if attr == "type":
            val = {0: "None", 1: "Li", 2: "Nm", 3: "Nc", 4: "Pb"}[val]
        if attr.endswith("_current"):
            val = val / 10.0
        return val


def read(ser: serial.Serial) -> Iterator[Packet]:  # pragma: no cover
    """Read packets from serial interface."""
    packet = bytearray()
    while True:
        for byte in ser.read():
            if byte == ord("}"):
                break
        if byte == ord("}"):
            break
    while True:
        for byte in ser.read():
            if byte == ord("{"):
                del packet[:]
            elif byte == ord("}"):
                data = Packet.from_buffer(packet)
                yield data
            else:
                if byte >= 128:
                    byte = byte - 128
                packet.append(byte)
