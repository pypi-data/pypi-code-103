#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure system commands and responses execute successfully."""


from threading import Event

import pytest

from stepseries import commands, responses, step400
from tests.conftest import HardwareIncremental


class TestSystemSettings(HardwareIncremental):
    # This test MUST run first to enable communication with the device
    @pytest.mark.order(1)
    def test_set_dest_ip(self, device: step400.STEP400, dest_ip_success: Event) -> None:
        device.set(commands.SetDestIP())
        assert dest_ip_success.wait(timeout=0.5), "hardware not detected"

    def test_get_version(self, device: step400.STEP400) -> None:
        resp = device.get(commands.GetVersion())
        assert isinstance(resp, responses.Version)

    def test_get_config_name(self, device: step400.STEP400) -> None:
        resp = device.get(commands.GetConfigName())
        assert isinstance(resp, responses.ConfigName)

    def test_report_error(self, device: step400.STEP400) -> None:
        device.set(commands.ReportError(enable=1))
        device.set(commands.ReportError(False))
