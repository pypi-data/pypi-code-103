#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure system commands and responses execute successfully."""


import time

import pytest

from stepseries import commands, step400
from tests.conftest import HardwareIncremental


@pytest.mark.skip_disconnected
class TestMotorControlSettings(HardwareIncremental):

    # Motor presets
    # Note: This test suite assumes a motor of 200 steps/rev
    run_motor: bool = False

    def test_run(self, device: step400.STEP400) -> None:
        if self.run_motor:
            device.set(commands.Run(3, 125))
            time.sleep(3)
            device.set(commands.Run(3, 0))
            time.sleep(3)
        else:
            pytest.skip("preset 'run_motor' is not set")

    def test_move(self, device: step400.STEP400) -> None:
        if self.run_motor:
            device.set(commands.Move(3, 1000))
            time.sleep(3)
        else:
            pytest.skip("preset 'run_motor' is not set")

    def test_goto(self, device: step400.STEP400) -> None:
        if self.run_motor:
            device.set(commands.GoTo(3, 2500))
            time.sleep(3)
        else:
            pytest.skip("preset 'run_motor' is not set")

    def test_goto_dir(self, device: step400.STEP400) -> None:
        if self.run_motor:
            device.set(commands.GoToDir(3, 0, 1000))
            time.sleep(3)
        else:
            pytest.skip("preset 'run_motor' is not set")

    def test_soft_stop(self, device: step400.STEP400) -> None:
        if self.run_motor:
            device.set(commands.Run(3, 125))
            time.sleep(3)
            device.set(commands.SoftStop(3))
            time.sleep(3)
        else:
            pytest.skip("preset 'run_motor' is not set")

    def test_hard_stop(self, device: step400.STEP400) -> None:
        if self.run_motor:
            device.set(commands.Run(3, 125))
            time.sleep(3)
            device.set(commands.HardStop(3))
            time.sleep(1)
        else:
            pytest.skip("preset 'run_motor' is not set")

    def test_soft_hiz(self, device: step400.STEP400) -> None:
        if self.run_motor:
            device.set(commands.Run(3, 125))
            time.sleep(3)
            device.set(commands.SoftHiZ(3))
            time.sleep(3)
        else:
            pytest.skip("preset 'run_motor' is not set")

    def test_hard_hiz(self, device: step400.STEP400) -> None:
        if self.run_motor:
            device.set(commands.Run(3, 125))
            time.sleep(3)
            device.set(commands.HardHiZ(3))
            time.sleep(1)
        else:
            pytest.skip("preset 'run_motor' is not set")
