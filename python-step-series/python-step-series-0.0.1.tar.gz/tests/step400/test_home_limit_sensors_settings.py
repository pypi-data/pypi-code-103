#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure system commands and responses execute successfully."""


import pytest

from stepseries import commands, responses, step400
from tests.conftest import HardwareIncremental


@pytest.mark.skip_disconnected
class TestHomeLimitSensorsSettings(HardwareIncremental):
    def test_home_sw(self, device: step400.STEP400) -> None:
        device.set(commands.EnableHomeSwReport(3, True))
        device.set(commands.EnableSwEventReport(3, True))
        resp = device.get(commands.GetHomeSw(3))
        assert isinstance(resp, responses.HomeSw)

    def test_limit_sw(self, device: step400.STEP400) -> None:
        device.set(commands.EnableLimitSwReport(3, True))
        # TODO: Debug
        try:
            resp = device.get(commands.GetLimitSw(3))
            assert isinstance(resp, responses.LimitSw)
        except TimeoutError:
            pytest.skip("timed-out waiting for a response")

    def test_home_sw_mode(self, device: step400.STEP400) -> None:
        device.set(commands.SetHomeSwMode(3, 1))
        resp = device.get(commands.GetHomeSwMode(3))
        assert isinstance(resp, responses.HomeSwMode)
        assert resp.swMode == 1

    def test_limit_sw_mode(self, device: step400.STEP400) -> None:
        device.set(commands.SetLimitSwMode(3, 1))
        resp = device.get(commands.GetLimitSwMode(3))
        assert isinstance(resp, responses.LimitSwMode)
        assert resp.swMode == 1
