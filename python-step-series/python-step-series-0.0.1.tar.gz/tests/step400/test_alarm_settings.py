#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure system commands and responses execute successfully."""


import pytest

from stepseries import commands, responses, step400
from tests.conftest import HardwareIncremental


@pytest.mark.skip_disconnected
class TestAlarmSettings(HardwareIncremental):
    def test_uvlo(self, device: step400.STEP400) -> None:
        device.set(commands.EnableUvloReport(4, False))
        resp = device.get(commands.GetUvlo(4))
        assert isinstance(resp, responses.Uvlo)

    def test_thermal_status(self, device: step400.STEP400) -> None:
        device.set(commands.EnableThermalStatusReport(3, True))
        resp = device.get(commands.GetThermalStatus(3))
        assert isinstance(resp, responses.ThermalStatus)
        device.set(commands.EnableThermalStatusReport(3, False))

    def test_over_current(self, device: step400.STEP400) -> None:
        device.set(commands.EnableOverCurrentReport(2, True))
        device.set(commands.SetOverCurrentThreshold(2, 18))
        resp = device.get(commands.GetOverCurrentThreshold(2))
        assert isinstance(resp, responses.OverCurrentThreshold)
        assert resp.overCurrentThreshold == 5937.5
        device.set(commands.SetOverCurrentThreshold(2, 15))
        device.set(commands.EnableOverCurrentReport(2, False))

    def test_stall_report(self, device: step400.STEP400) -> None:
        device.set(commands.EnableStallReport(1, True))
        device.set(commands.SetStallThreshold(1, 6))
        resp = device.get(commands.GetStallThreshold(1))
        assert isinstance(resp, responses.StallThreshold)
        assert resp.stallThreshold == 2187.5
        device.set(commands.SetStallThreshold(1, 31))
        device.set(commands.EnableStallReport(1, False))

    def test_prohibit_motion_on_home_sw(self, device: step400.STEP400) -> None:
        device.set(commands.SetProhibitMotionOnHomeSw(4, True))
        resp = device.get(commands.GetProhibitMotionOnHomeSw(4))
        assert isinstance(resp, responses.ProhibitMotionOnHomeSw)
        assert resp.enable is True
        device.set(commands.SetProhibitMotionOnHomeSw(4, False))

    def test_prohibit_motion_on_limit_sw(self, device: step400.STEP400) -> None:
        device.set(commands.SetProhibitMotionOnLimitSw(4, True))
        resp = device.get(commands.GetProhibitMotionOnLimitSw(4))
        assert isinstance(resp, responses.ProhibitMotionOnLimitSw)
        assert resp.enable is True
        device.set(commands.SetProhibitMotionOnLimitSw(4, False))
