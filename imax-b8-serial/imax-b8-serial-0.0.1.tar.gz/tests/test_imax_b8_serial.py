"""Limited unit tests without hardware."""

from typing import Any

import imax_b8_serial  # noqa: F401


def _todict(x: Any) -> Any:
    return dict((name, x[name]) for name in dir(x) if not name.startswith("_"))


def test_packet() -> None:
    """Test packet decoding."""
    packet = _todict(imax_b8_serial.Packet())
    packet["settings"] = _todict(packet["settings"])
    assert packet == {
        "active": 0,
        "backlight": "0%",
        "capacity_cuttoff": 0.0,
        "charge": 0.0,
        "current": 0.0,
        "input_cuttoff": 0,
        "input_voltage": 0.0,
        "lipo_cell0": 0.0,
        "lipo_cell1": 0.0,
        "lipo_cell2": 0.0,
        "lipo_cell3": 0.0,
        "lipo_cell4": 0.0,
        "lipo_cell5": 0.0,
        "lipo_cell6": 0.0,
        "lipo_cell7": 0.0,
        "lipo_cells": 0,
        "lipo_charge_current": 0.0,
        "lipo_discharge_current": 0.0,
        "mode": "Discharge",
        "nicd_charge_current": 0.0,
        "nicd_cycle": 0,
        "nicd_cycles": 0,
        "nicd_discharge_current": 0.0,
        "nicd_discharge_cutoff": 0.0,
        "nicd_sensitivity": 0,
        "nimh_charge_current": 0.0,
        "nimh_cycle": 0,
        "nimh_cycles": 0,
        "nimh_dischage_cutoff": 0.0,
        "nimh_discharge_current": 0.0,
        "nimh_sensitivity": 0,
        "pb_cells": 0,
        "pb_charge_current": 0.0,
        "safty_timer": 0,
        "settings": {
            "Buzz": 0,
            "Capacity Cutoff": 0,
            "Key beep": 0,
            "Temp Cutoff": 0,
            "a": 0,
            "c": 0,
            "d": 0,
            "e": 0,
        },
        "temp_cutoff": 0,
        "temp_external": 0.0,
        "temp_internal": 0.0,
        "type": "None",
        "voltage": 0.0,
        "waste_time": 0,
    }
