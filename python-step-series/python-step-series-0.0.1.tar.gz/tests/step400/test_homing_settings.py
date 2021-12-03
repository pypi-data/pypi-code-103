#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure system commands and responses execute successfully."""


import pytest

from stepseries import commands, responses, step400
from tests.conftest import HardwareIncremental


@pytest.mark.skip_disconnected
class TestHomingSettings(HardwareIncremental):

    # Presets for running homing commands
    direction: int = None  # forward: 1; reverse: 0
    speed: float = None  # 0 - 15625; default is 100 steps/secs
    gu_timeout: int = None  # goUntil timeout; 0 - 65535; default is 10000ms
    sw_timeout: int = None  # 0 - 65535; default is 5000ms
    motor: int = None  # 1 - 4
    run_motor: bool = False  # Run the motor with the above presets

    def test_homing_presets(self) -> None:
        err_msg = "before running homing tests, the presets need to be configured"
        if self.direction is None:
            raise ValueError(err_msg)
        if self.speed is None:
            raise ValueError(err_msg)
        if self.gu_timeout is None:
            raise ValueError(err_msg)
        if self.sw_timeout is None:
            raise ValueError(err_msg)
        if self.motor is None:
            raise ValueError(err_msg)

    def test_homing_direction(self, device: step400.STEP400) -> None:
        device.set(commands.SetHomingDirection(self.motor, self.direction))
        resp = device.get(commands.GetHomingDirection(self.motor))
        assert isinstance(resp, responses.HomingDirection)
        assert resp.homingDirection == self.direction

    def test_homing_speed(self, device: step400.STEP400) -> None:
        device.set(commands.SetHomingSpeed(self.motor, self.speed))
        resp = device.get(commands.GetHomingSpeed(self.motor))
        assert isinstance(resp, responses.HomingSpeed)
        assert resp.homingSpeed == self.speed

    def test_go_until_timeout(self, device: step400.STEP400) -> None:
        device.set(commands.SetGoUntilTimeout(self.motor, self.gu_timeout))
        resp = device.get(commands.GetGoUntilTimeout(self.motor))
        assert isinstance(resp, responses.GoUntilTimeout)
        assert resp.timeout == self.gu_timeout

    def test_release_sw_timeout(self, device: step400.STEP400) -> None:
        device.set(commands.SetReleaseSwTimeout(self.motor, self.sw_timeout))
        resp = device.get(commands.GetReleaseSwTimeout(self.motor))
        assert isinstance(resp, responses.ReleaseSwTimeout)
        assert resp.timeout == self.sw_timeout

    def test_homing(self, device: step400.STEP400) -> None:
        if self.run_motor:
            device.set(commands.Homing(4))
        else:
            pytest.skip("preset 'run_motor' is not set")
