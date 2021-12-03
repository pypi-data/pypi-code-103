#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure system commands and responses execute successfully."""


from math import isclose  # Due to precision, we cannot compare floats directly

import pytest

from stepseries import commands, responses, step400
from tests.conftest import HardwareIncremental


@pytest.mark.skip_disconnected
class TestMotorDriverSettings(HardwareIncremental):
    def test_microstep_mode(self, device: step400.STEP400) -> None:
        device.set(commands.SetMicrostepMode(1, 5))
        resp = device.get(commands.GetMicrostepMode(1))
        assert isinstance(resp, responses.MicrostepMode)
        assert resp.STEP_SEL == 5
        device.set(commands.SetMicrostepMode(1, 7))

    def test_low_speed_optimize_threshold(self, device: step400.STEP400) -> None:
        device.set(commands.EnableLowSpeedOptimize(4, True))
        device.set(commands.SetLowSpeedOptimizeThreshold(4, 555.5))
        resp = device.get(commands.GetLowSpeedOptimizeThreshold(4))
        assert isinstance(resp, responses.LowSpeedOptimizeThreshold)
        assert isclose(resp.lowSpeedOptimizeThreshold, 555.5, rel_tol=0.1)
        device.set(commands.SetLowSpeedOptimizeThreshold(4, 0.0))
        device.set(commands.EnableLowSpeedOptimize(4, False))

    def test_busy(self, device: step400.STEP400) -> None:
        device.set(commands.EnableBusyReport(2, False))
        resp = device.get(commands.GetBusy(2))
        assert isinstance(resp, responses.Busy)

    def test_hiz(self, device: step400.STEP400) -> None:
        device.set(commands.EnableHiZReport(1, True))
        resp = device.get(commands.GetHiZ(1))
        assert isinstance(resp, responses.HiZ)
        device.set(commands.EnableHiZReport(1, False))

    def test_motor_status(self, device: step400.STEP400) -> None:
        device.set(commands.EnableMotorStatusReport(4, False))
        resp = device.get(commands.GetMotorStatus(4))
        assert isinstance(resp, responses.MotorStatus)

    def test_get_adc_val(self, device: step400.STEP400) -> None:
        resp = device.get(commands.GetAdcVal(2))
        assert isinstance(resp, responses.AdcVal)

    def test_get_status(self, device: step400.STEP400) -> None:
        resp = device.get(commands.GetStatus(3))
        assert isinstance(resp, responses.Status)

    def test_get_config_register(self, device: step400.STEP400) -> None:
        resp = device.get(commands.GetConfigRegister(1))
        assert isinstance(resp, responses.ConfigRegister)

    def test_reset_motor_driver(self, device: step400.STEP400) -> None:
        device.set(commands.ResetMotorDriver(4))
        device.set(commands.ResetMotorDriver(3))
        device.set(commands.ResetMotorDriver(2))
        device.set(commands.ResetMotorDriver(1))
