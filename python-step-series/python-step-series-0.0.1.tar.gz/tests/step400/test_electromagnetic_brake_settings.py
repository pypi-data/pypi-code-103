#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure system commands and responses execute successfully."""


import pytest

from stepseries import commands, responses, step400
from tests.conftest import HardwareIncremental


@pytest.mark.skip_disconnected
class TestElectromagneticBrakeSettings(HardwareIncremental):

    # Electromagnetic brake presets
    brake_connected: bool = False

    def test_enable_electromagnet_brake(self, device: step400.STEP400) -> None:
        if self.brake_connected:
            device.set(commands.EnableElectromagnetBrake(1, True))
        else:
            pytest.skip("preset 'brake_connected' is not set")

    def test_activate(self, device: step400.STEP400) -> None:
        if self.brake_connected:
            device.set(commands.Activate(1, True))
        else:
            pytest.skip("preset 'brake_connected' is not set")

    def test_free(self, device: step400.STEP400) -> None:
        if self.brake_connected:
            device.set(commands.Free(1, True))
        else:
            pytest.skip("preset 'brake_connected' is not set")

    def test_brake_transition_duration(self, device: step400.STEP400) -> None:
        device.set(commands.SetBrakeTransitionDuration(1, 1250))
        resp = device.get(commands.GetBrakeTransitionDuration(1))
        assert isinstance(resp, responses.BrakeTransitionDuration)
        assert resp.duration == 1250
