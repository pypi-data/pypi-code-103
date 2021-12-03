#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ensure OSC responses from the controller build correctly."""


from stepseries import responses


def test_position() -> None:
    message = "/position 1 -900875"
    osc_message1 = responses.Position(*message.split())
    osc_message2 = responses.Position(message)

    gospel = responses.Position("/position", "1", "-900875")
    assert osc_message1 == gospel
    assert osc_message2 == gospel


def test_mark() -> None:
    message = "/mark 3 74585"
    osc_message1 = responses.Mark(*message.split())
    osc_message2 = responses.Mark(message)

    gospel = responses.Mark("/mark", "3", "74585")
    assert osc_message1 == gospel
    assert osc_message2 == gospel
