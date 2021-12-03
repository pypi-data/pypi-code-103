#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure system commands and responses raise errors properly."""


import pytest

from stepseries import commands, responses, step400


@pytest.mark.skip_disconnected
def test_device_errors(device: step400.STEP400) -> None:
    with pytest.raises(TypeError):
        device.set(commands.GetVersion())

    with pytest.raises(TypeError):
        device.get(commands.SetDestIP())

    with pytest.raises(AttributeError):
        device.on("Hello world", lambda x: None)

    with pytest.raises(TypeError):
        device.on(None, "Hello world")

    @commands.dataclass
    class DummyGetCommand(commands.OSCGetCommand):
        address: str = commands.field(default="/getDummy", init=False)
        motorID: int

    with pytest.raises(responses.ErrorOSC):
        device.set(commands.ReportError(True))  # Ensure error reporting is enabled
        device.get(DummyGetCommand(1))
