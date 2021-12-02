#!/usr/bin/env python3
#   encoding: utf-8

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

import argparse
import sys
import time

from balladeer import Story

import tas
from tas.drama import Sympathy
from tas.types import Operation
from tas.world import Tea

version = tas.__version__


class TeaAndSympathy(Story):

    def __init__(self, cfg=None, **kwargs):
        super().__init__(**kwargs)
        world = Tea(**kwargs)
        self.drama = [Sympathy(world, **kwargs)]

    @property
    def active(self):
        return [i for i in self.drama.values() if i.active]


def parser():
    rv = argparse.ArgumentParser()
    rv.add_argument(
        "--debug", action="store_true", default=False,
        help="Write generated dialogue for debugging."
    )
    rv.add_argument(
        "--quick", action="store_true", default=False,
        help="Don't perform timed animations."
    )
    return rv


def main(opts):
    story = TeaAndSympathy(**vars(opts))
    text = ""
    presenter = None
    while story.active:
        presenter = story.represent(text, facts=story.context.facts, previous=presenter)
        if opts.debug:
            print(presenter.text, file=sys.stderr)
            print(*presenter.frames, sep="\n", file=sys.stderr)

        for frame in filter(None, presenter.frames):
            animation = presenter.animate(
                frame, dwell=presenter.dwell, pause=presenter.pause
            )
            if not animation:
                continue

            for line, duration in story.render_frame_to_terminal(animation):
                print(line, "\n")
                if not opts.quick:
                    time.sleep(duration)

            if story.context.get_state(Operation) != Operation.frames:
                break

        if story.context.get_state(Operation) == Operation.finish:
            break

        cmd = input("{0} ".format(story.context.prompt))
        text = story.context.deliver(cmd, presenter=presenter)


def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)


if __name__ == "__main__":
    run()
