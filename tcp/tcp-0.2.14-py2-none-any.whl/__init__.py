# -*- coding: utf-8 -*-
#
#   TCP: Transmission Control Protocol
#
#                                Written in 2020 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2020 Albert Moky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================


from startrek import Hub, Channel, Connection, ConnectionDelegate
from startrek import ConnectionState, ConnectionStateMachine
from startrek import BaseHub, BaseChannel, BaseConnection, ActiveConnection

from startrek import Ship, ShipDelegate, Arrival, Departure, DeparturePriority
from startrek import Docker, Gate, GateStatus, GateDelegate

from startrek import ArrivalShip, ArrivalHall, DepartureShip, DepartureHall
from startrek import Dock, LockedDock, StarDocker, StarGate

from .startrek import PlainArrival, PlainDeparture, PlainDocker
from .channel import StreamChannel
from .hub import StreamHub, ServerHub, ClientHub

name = "TCP"

__author__ = 'Albert Moky'

__all__ = [

    'Hub', 'Channel', 'Connection', 'ConnectionDelegate',
    'ConnectionState', 'ConnectionStateMachine',
    'BaseHub', 'BaseChannel', 'BaseConnection', 'ActiveConnection',
    'Ship', 'ShipDelegate', 'Arrival', 'Departure', 'DeparturePriority',
    'Docker', 'Gate', 'GateStatus', 'GateDelegate',
    'ArrivalShip', 'ArrivalHall', 'DepartureShip', 'DepartureHall',
    'Dock', 'LockedDock', 'StarDocker', 'StarGate',

    'PlainArrival', 'PlainDeparture', 'PlainDocker',

    'StreamChannel',
    'StreamHub',
    'ServerHub', 'ClientHub',
]
