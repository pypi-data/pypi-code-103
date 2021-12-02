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

import unittest

from balladeer import Name
from balladeer import Presenter
from balladeer import Renderer
from balladeer import Settings

from tas.drama import Sympathy
from tas.types import Container
from tas.types import Journey
from tas.types import Location
from tas.types import Operation
from tas.world import Tea


class SympathyTests(unittest.TestCase):

    @staticmethod
    def turn(cmd, drama, settings, text=None, previous=None):
        drama.interlude(drama.folder, previous and previous.index, previous and previous.ensemble)
        presenter = Presenter.build_presenter(
            drama.folder, text, facts=drama.facts,
            ensemble=drama.ensemble + [drama, settings]
        )
        lines = []
        for frame in filter(None, presenter.frames):
            animation = presenter.animate(
                frame, dwell=presenter.dwell, pause=presenter.pause
            )
            if not animation:
                continue

            for line, duration in Renderer.render_frame_to_terminal(animation):
                lines.append(line)

            if drama.get_state(Operation) != Operation.frames:
                break

        text = drama.deliver(cmd, presenter=presenter)
        return presenter, animation, lines, text

    def setUp(self):
        self.settings = Settings()
        world = Tea()
        self.drama = Sympathy(world)

    def test_help(self):
        text = None
        presenter = None
        self.assertEqual(2, len([i for i in self.drama.ensemble if isinstance(i, Container)]))
        self.assertEqual(1, len([i for i in self.drama.world.local.each if isinstance(i, Container)]))

        presenter, animation, lines, text = self.turn("help", self.drama, self.settings, text, previous=presenter)
        self.assertNotIn(self.drama.do_inspect, self.drama.active)
        self.assertNotIn("inspect", text.lower(), text)
        self.assertNotIn(self.drama.do_get, self.drama.active)
        self.assertFalse(any(i in text.lower() for i in ("get", "grab", "pick", "take")), text)

        presenter, animation, lines, text = self.turn("look", self.drama, self.settings, text, previous=presenter)
        mug = next(iter(self.drama.world.lookup["mug"]))
        self.assertIn(mug, self.drama.world.visible.each)

        presenter, animation, lines, text = self.turn("help", self.drama, self.settings, text, previous=presenter)
        self.assertIn("inspect", text.lower(), text)
        self.assertIn(self.drama.do_get, self.drama.active)
        self.assertIn(self.drama.do_get, self.drama.active)
        self.assertTrue(any(i in text.lower() for i in ("get", "grab", "pick", "take")), text)

    def test_look(self):
        cmds = ["look", "inspect mug", "inspect louise", "get mug", "inspect louise", "look"]
        text = None
        presenter = None
        mug = next(iter(self.drama.world.lookup["mug"]))

        self.assertNotIn(self.drama.do_get, self.drama.active)
        self.assertNotIn(self.drama.do_go, self.drama.active)
        self.assertNotIn(self.drama.do_inspect, self.drama.active)

        for n, cmd in enumerate(cmds):
            presenter, animation, lines, text = self.turn(cmd, self.drama, self.settings, text, previous=presenter)
            with self.subTest(n=n, cmd=cmd, phase="post"):
                if n in (0, 5):
                    self.assertIn("hall", text.lower())
                if n != 2:
                    self.assertIn("mug", text.lower())

        self.assertIn(self.drama.do_get, self.drama.active)
        self.assertIn(self.drama.do_go, self.drama.active)
        self.assertIn(self.drama.do_inspect, self.drama.active)
        self.assertIn(mug, self.drama.world.visible.each)

    def test_get(self):
        cmds = ["look", "inspect mug", "get mug", "help"]
        text = None
        presenter = None
        mug = next(iter(self.drama.world.lookup["mug"]))
        for n, cmd in enumerate(cmds):

            with self.subTest(n=n, cmd=cmd, phase="pre"):
                if n == 0:
                    self.assertNotIn(self.drama.do_get, self.drama.active)

            presenter, animation, lines, text = self.turn(cmd, self.drama, self.settings, text, previous=presenter)

            with self.subTest(n=n, cmd=cmd, phase="post"):
                if n == 0:
                    self.assertIn(self.drama.do_get, self.drama.active)
                elif n == 1:
                    self.assertIn("Luton", text, self.drama.world.visible.each)
                elif n == 2:
                    self.assertEqual(Location.inventory, mug.get_state(Location), text)

    def test_smoke_cigarette(self):
        cmds = [
            "look", "get mug", "inspect mug", "hall", "kitchen", "", "", "", "help",
            "smoke cigarette", "", "", "", "", ""
        ]
        text = None
        presenter = None
        for n, cmd in enumerate(cmds):
            try:
                presenter, animation, lines, text = self.turn(
                    cmd, self.drama, self.settings, text, previous=presenter
                )
            except AttributeError:
                print(n, cmd, animation)
                raise

            with self.subTest(n=n, cmd=cmd, phase="post"):
                if n == 0:
                    self.assertNotIn(self.drama.do_propose, self.drama.active)
                elif n == 2:
                    self.assertIn(self.drama.do_propose, self.drama.active)
                elif n == 8:
                    self.assertEqual("help", cmd)
                    self.assertEqual(2, len(self.drama.world.fruition["inception"]), self.drama.world.fruition)
                    self.assertIn("make tea", text.lower())
                    self.assertIn("smoke cigarette", text.lower())
                elif n == 12:
                    self.assertEqual(1, len(self.drama.world.fruition["inception"]))
                    self.assertEqual(1, len(self.drama.world.fruition["transition"]))
                elif n == 13:
                    self.assertEqual(1, len(self.drama.world.fruition["completion"]))
                    self.assertEqual(0, next(iter(self.drama.world.lookup["sophie"])).state)

    def test_make_tea(self):
        cmds = [
            "look", "get mug", "inspect mug", "hall", "kitchen", "", "", "", "help",
            "make tea", "look",
            "", "help",
            "help",
            "no",
        ] + [""] * 7 + [
            "drop mug"
        ]
        text = None
        presenter = None
        for n, cmd in enumerate(cmds):
            presenter, animation, lines, text = self.turn(
                cmd, self.drama, self.settings, text, previous=presenter
            )

            with self.subTest(n=n, cmd=cmd, phase="post"):
                if n == 0:
                    self.assertNotIn(self.drama.do_propose, self.drama.active)
                elif n == 2:
                    self.assertIn(self.drama.do_propose, self.drama.active)
                elif n == 8:
                    self.assertEqual("help", cmd)
                    self.assertEqual(2, len(self.drama.world.fruition["inception"]), self.drama.world.fruition)
                    self.assertIn("make tea", text.lower())
                    self.assertIn("smoke cigarette", text.lower())
                elif n == 12:
                    self.assertEqual("help", cmd)
                    self.assertEqual(1, len(self.drama.world.fruition["inception"]))
                    self.assertEqual(1, len(self.drama.world.fruition["discussion"]))
                elif n == 13:
                    self.assertEqual("help", cmd)
                    self.assertEqual(1, len(self.drama.world.fruition["discussion"]))
                    self.assertIn("yes", text.lower())
                    self.assertIn("no", text.lower())
                    self.assertEqual(0, next(iter(self.drama.world.lookup["sophie"])).state)
                elif n == 14:
                    self.assertEqual(1, len(self.drama.world.fruition["elaboration"]))
                elif n == 15:
                    self.assertEqual(1, next(iter(self.drama.world.lookup["sophie"])).state)
                    self.assertEqual(1, len(self.drama.world.fruition["construction"]))
                    self.assertTrue(self.drama.world.player.memories)

    def test_go(self):
        cmds = ["go hall", "go bedroom", "go hall", "go stairs", "go kitchen", "go hall", "go bedroom"]
        text = None
        presenter = None
        self.drama.active.add(self.drama.do_go)
        for n, cmd in enumerate(cmds):
            presenter, animation, lines, text = self.turn(cmd, self.drama, self.settings, text, previous=presenter)

            with self.subTest(n=n, cmd=cmd):
                self.assertIn(cmd.split()[-1], text.lower())

    def test_mentor(self):
        cmds = ["look", "get mug", "hall", "kitchen", "", "", ""]
        text = None
        presenter = None
        mug = next(iter(self.drama.world.lookup["mug"]))
        for n, cmd in enumerate(cmds):
            presenter, animation, lines, text = self.turn(cmd, self.drama, self.settings, text, previous=presenter)
        self.assertIn(mug, self.drama.world.visible.each)
        self.assertEqual(Journey.ordeal, self.drama.get_state(Journey))

    def test_world_lookup(self):
        self.assertIn("sophie", self.drama.world.lookup)
        self.assertIn("kettle", self.drama.world.lookup)
        self.assertIn("smoke cigarette", self.drama.world.lookup, self.drama.world.lookup)
