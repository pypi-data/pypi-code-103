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

import bisect
from collections import Counter
from collections import defaultdict
from collections import namedtuple
import functools
import itertools
import random
import re
import textwrap

from balladeer import CommandParser
from balladeer import Drama
from balladeer import Fruition
from balladeer import Gesture
from balladeer import SceneScript

from tas.types import Availability
from tas.types import Character
from tas.types import Container
from tas.types import Journey
from tas.types import Location
from tas.types import Motivation
from tas.types import Operation
from tas.world import Tea


class Sympathy(Drama):

    @property
    def ensemble(self):
        return list(self.world.lookup.each)

    @property
    def folder(self):
        return SceneScript.Folder(
            pkg="tas.dlg",
            description="Tea and Sympathy",
            metadata={},
            paths=[
                "01_inception.rst",
                "02_elaboration.rst",
                "03_construction.rst",
                "04_transition.rst",
                "05_completion.rst",
                "06_discussion.rst",
                "09_cancelled.rst",
                "10_resolution.rst",
                "11_conclusion.rst",
                "12_intervention.rst",
                "00_introduction.rst",
            ],
            interludes=None
        )

    def __init__(self, world, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.active = self.active.union({
            self.do_again, self.do_look,
            self.do_counter,
            self.do_confirm, self.do_disavow,
            self.do_abandon,
            self.do_help, self.do_history,
            self.do_quit
        })
        self.default_fn = self.do_next

        self.world = world
        self.set_state(Journey.mentor, Operation.prompt)

    def interlude(self, folder, index, *args, **kwargs):
        return {}

    def do_propose(self, this, text, presenter, obj: "world.fruition[inception]", *args, **kwargs):
        """
        {obj!s}

        """
        # TODO: Create a memory of subject=player, object=obj.contents, state=?
        obj.state = Fruition.elaboration
        self.active.discard(this) # TODO: Place other option removed.
        return obj

    def do_counter(self, this, text, presenter, obj: "world.fruition[discussion]", *args, **kwargs):
        """
        {obj.counter}

        """
        obj.state = Fruition.elaboration
        return obj

    def do_confirm(self, this, text, presenter, obj: "world.fruition[discussion]", *args, **kwargs):
        """
        {obj.confirm}

        """
        obj.state = Fruition.construction
        return obj

    def do_disavow(self, this, text, presenter, obj: "world.fruition[construction]", *args, **kwargs):
        """
        {obj.disavow}

        """
        obj.state = Fruition.defaulted
        return obj

    def do_abandon(self, this, text, presenter, obj: "world.fruition[transition]", *args, **kwargs):
        """
        {obj.abandon}

        """
        obj.state = Fruition.cancelled
        return obj

    def do_again(self, this, text, presenter, *args, **kwargs):
        """
        again | back

        """
        n = len(list(itertools.takewhile(
            lambda x: x.name == this.__name__, self.history
        ))) + 1
        self.state = self.next_states(n)[0]
        return "again..."

    def do_get(self, this, text, presenter, obj: "world.visible[Container]", *args, **kwargs):
        """
        get {obj.names[0].noun}
        grab {obj.names[0].noun}
        take {obj.names[0].noun}
        pick up {obj.names[0].noun}

        """
        obj.state = Location.inventory
        self.active.discard(this)
        return f"{self.world.player.name} picks up {obj.names[0].article.definite} {obj.names[0].noun}.",

    def do_go(self, this, text, presenter, *args, locn: "world.player.location.options", **kwargs):
        """
        enter {locn.value[0]} | enter {locn.value[1]}
        go {locn.value[0]} | go {locn.value[1]} | go {locn.value[2]} | go {locn.value[3]} | go {locn.value[4]}
        {locn.value[0]} | {locn.value[1]} | {locn.value[2]} | {locn.value[3]} | {locn.value[4]}

        """
        if locn == Location.stairs:
            yield f"{self.world.player.name} looks upward."
            yield "The stairs lead to an attic gallery, and Sophie's room."
            yield f"{self.world.player.name} hesitates."
            yield "{0} doesn't want to go up there.".format(self.world.player.names[0].pronoun.subject.title())
        else:
            gone = (i for i in self.history if i.name == this.__name__)
            never_been = locn != Location.bedroom and not any(i for i in gone if i.kwargs["locn"] == locn)
            self.state = 0 if never_been else 1
            self.world.player.state = locn
            yield f"{self.world.player.name} goes into the {locn.title}."

    def do_help(self, this, text, presenter, *args, **kwargs):
        """
        help
        what | what do i do

        """
        self.state = Operation.paused
        options = {
            fn.__name__: list(CommandParser.expand_commands(fn, self.ensemble, parent=self))
            for fn in self.active
        }
        for k, v in sorted(options.items()):
            cmds = []
            for cmd, (fn, kwargs) in v:
                if fn is self.do_go and len(cmd.split()) == 1:
                    continue

                if all(
                    isinstance(i, Location) or
                    i is self.world.player or
                    i in self.world.visible.each
                    for i in kwargs.values()
                ):
                    cmds.append(cmd)

            if cmds:
                if k in ("do_propose", "do_counter", "do_confirm", "do_disavow", "do_abandon"):
                    yield from ("* {0}".format(i) for i in cmds if i != str(tuple()))
                else:
                    yield "* {0}".format(random.choice(cmds))

    def do_history(self, this, text, presenter, *args, **kwargs):
        """
        history

        """
        self.state = Operation.paused
        yield from ("* {0.args[0]}".format(i) for i in self.history if i.args[0])

    def do_inspect(self, this, text, presenter, obj: "world.visible.each", *args, **kwargs):
        """
        inspect {obj.names[0].noun}

        """
        if obj.names[0].noun.lower() == "mug":
            self.active.add(self.do_propose)

        self.state = Operation.paused
        yield obj.description.format(obj, **self.facts)

        if obj is self.world.player:
            items = [
                i for i in self.ensemble
                if i.get_state(Location) == Location.inventory and i.get_state(Availability) == Availability.allowed
            ]
            if items:
                yield "\nCarrying:\n"
                yield from ("* {0}".format(i) for i in items)

    def do_look(self, this, text, presenter, *args, **kwargs):
        """
        look | look around
        where | where am i | where is it

        """
        self.state = Operation.paused
        self.active.add(self.do_get)
        self.active.add(self.do_go)
        self.active.add(self.do_inspect)
        for i in self.world.visible.each:
            if i is not self.world.player:
                try:
                    yield "* {0.names[0].noun}".format(i)
                except AttributeError:
                    pass  # Expect a gesture

        yield from ("* {0}".format(i.label.title()) for i in self.world.player.location.options)

    def do_next(self, this, text, presenter, *args, **kwargs):
        """
        more | next

        """
        try:
            self.state = self.next_states(0)[1]
        except Exception:
            pass

        return random.choice([
            f"{self.world.player.name} hesitates.",
            f"{self.world.player.name} pauses.",
            f"{self.world.player.name} waits in the {self.world.player.location.title} for a moment.",
        ])

    def do_quit(self, this, text, presenter, *args, **kwargs):
        """
        quit

        """
        self.state = Operation.ending
