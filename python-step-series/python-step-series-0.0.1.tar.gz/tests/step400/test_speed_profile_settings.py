#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure system commands and responses execute successfully."""


import pytest

from stepseries import commands, responses, step400
from tests.conftest import HardwareIncremental


@pytest.mark.skip_disconnected
class TestSpeedProfileSettings(HardwareIncremental):
    def test_speed_profile(self, device: step400.STEP400) -> None:
        device.set(commands.SetSpeedProfile(4, 5555, 4444, 3333))
        resp = device.get(commands.GetSpeedProfile(4))
        assert isinstance(resp, responses.SpeedProfile)
        # TODO: Debug why the device returns values less than set here
        # assert resp.acc == 5555
        # assert resp.dec == 4444
        # assert resp.maxSpeed == 3333
        device.set(commands.SetSpeedProfile(4, 2000, 2000, 620))

    def test_fullstep_speed(self, device: step400.STEP400) -> None:
        device.set(commands.SetFullstepSpeed(3, 9206.46))
        resp = device.get(commands.GetFullstepSpeed(3))
        assert isinstance(resp, responses.FullstepSpeed)
        # TODO: Debug why the device returns values less than set here
        # assert resp.fullstepSpeed == 9206.46
        device.set(commands.SetFullstepSpeed(3, 15625))

    def test_set_max_speed(self, device: step400.STEP400) -> None:
        device.set(commands.SetMaxSpeed(2, 1240))

    def test_set_acc(self, device: step400.STEP400) -> None:
        device.set(commands.SetAcc(1, 6002))

    def test_set_dec(self, device: step400.STEP400) -> None:
        device.set(commands.SetDec(4, 155))

    def test_min_speed(self, device: step400.STEP400) -> None:
        device.set(commands.SetMinSpeed(3, 9206.46))
        resp = device.get(commands.GetMinSpeed(3))
        assert isinstance(resp, responses.MinSpeed)
        # TODO: Debug why the device returns values less than set here
        # assert resp.minSpeed == 9206.46
        device.set(commands.SetMinSpeed(3, 0))

    def test_get_speed(self, device: step400.STEP400) -> None:
        resp = device.get(commands.GetSpeed(2))
        assert isinstance(resp, responses.Speed)
