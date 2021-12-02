#!/usr/bin/env python3
# encoding: utf-8

# This is a technical demo and teaching example for the turberfield-catchphrase library.
# Copyright (C) 2021 D E Haynes

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from collections import defaultdict
from collections import namedtuple
import enum
import random

from balladeer import Named

from turberfield.dialogue.types import Stateful


class Motivation(enum.Enum):

    acting = enum.auto()
    player = enum.auto()


class Operation(enum.Enum):

    begins = enum.auto()
    frames = enum.auto()
    paused = enum.auto()
    prompt = enum.auto()
    ending = enum.auto()
    finish = enum.auto()


class Journey(enum.Enum):

    mentor = enum.auto()
    ordeal = enum.auto()
    reward = enum.auto()


class Availability(enum.Enum):

    allowed = enum.auto()
    fixture = enum.auto()
    removed = enum.auto()


class Location(enum.Enum):

    bedroom = ["bedroom"]
    hall = ["hall", "hallway"]
    kitchen = ["kitchen"]
    stairs = ["stairs", "stairway", "up", "up stairs", "upstairs"]
    inventory = None

    @property
    def label(self):
        return self.value[0]

    @property
    def title(self):
        return self.label.title()

    @property
    def options(self):
        topology = {
            Location.bedroom: [Location.hall],
            Location.hall: [Location.bedroom, Location.kitchen, Location.stairs],
            Location.kitchen: [Location.hall],
        }
        return topology.get(self, [])


class Located(Stateful):

    @property
    def location(self):
        return self.get_state(Location)


class Character(Named, Located):

    @property
    def location(self):
        return self.get_state(Location)


class Container(Named, Located): pass
