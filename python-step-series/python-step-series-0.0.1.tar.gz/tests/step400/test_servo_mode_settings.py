#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure system commands and responses execute successfully."""


import pytest

from stepseries import commands, responses, step400
from tests.conftest import HardwareIncremental


@pytest.mark.skip_disconnected
class TestServoModeSettings(HardwareIncremental):
    def test_enable_servo_mode(self, device: step400.STEP400) -> None:
        device.set(commands.EnableServoMode(2, True))

    def test_server_param(self, device: step400.STEP400) -> None:
        device.set(commands.SetServoParam(2, 12.5, 15.0, 17.5))
        resp = device.get(commands.GetServoParam(2))
        assert isinstance(resp, responses.ServoParam)
        assert resp.kP == 12.5
        assert resp.kI == 15.0
        assert resp.kD == 17.5

    def test_set_target_position(self, device: step400.STEP400) -> None:
        device.set(commands.SetTargetPosition(2, -28687))

    def test_set_target_position_list(self, device: step400.STEP400) -> None:
        device.set(commands.SetTargetPositionList(1401, 5529, 4363, 6852))
