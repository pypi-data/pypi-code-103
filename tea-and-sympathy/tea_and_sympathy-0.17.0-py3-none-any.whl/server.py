#!/usr/bin/env python3
# encoding: utf-8

# This is a technical demo and teaching example for the Balladeer library.
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
import asyncio
from collections import deque
from collections import namedtuple
import datetime
import logging
import re
import socket
import sys
import uuid

from aiohttp import web
import pkg_resources

from balladeer import Presenter
from turberfield.utils.misc import log_setup

import tas
from tas.story import TeaAndSympathy
from tas.types import Operation

HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
}
VALIDATION = {
    "email": re.compile(
        "[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]"
        "+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\\.[a-zA-Z0-9]"
        "(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+"
        # http://www.w3.org/TR/html5/forms.html#valid-e-mail-address
    ),
    "name": re.compile("[A-Z a-z]{2,42}"),
    "session": re.compile("[0-9a-f]{32}"),
}

Session = namedtuple("Session", ["ts", "story"])

async def start_tasks(app):
    app["janitor"] = asyncio.create_task(janitor(app))


async def cleanup_tasks(app):
    app["janitor"].cancel()
    await app["janitor"]


async def janitor(app):
    log = logging.getLogger("janitor")
    limit = datetime.timedelta(minutes=3)
    while True:
        now = datetime.datetime.now()
        orphans = [
            i for i in app["sessions"].values()
            if (now - i.ts) > limit and i.story.context.turns < 4
        ]
        for i in orphans:
            log.info("Discard {0.story.id} after turn {0.story.context.turns}".format(i))
            del app["sessions"][i.story.id]
        await asyncio.sleep(10)


async def get_root(request):
    story = TeaAndSympathy()
    story.presenter = story.represent("", facts=story.context.facts)
    session = Session(datetime.datetime.utcnow(), story)
    request.app["sessions"][story.id] = session
    raise web.HTTPFound("/{0.id.hex}".format(story), headers=HEADERS)


async def get_metrics(request):
    data = {
        "host": {"name": socket.gethostname()},
        "sessions": [
            {
                "uid": str(s.story.id),
                "start": s.ts.isoformat(),
                "turns": s.story.context.turns
            }
            for s in request.app["sessions"].values()
        ]
    }
    return web.json_response(data)


async def get_session(request):
    uid = uuid.UUID(hex=request.match_info["session"])
    try:
        session = request.app["sessions"][uid]
    except KeyError:
        raise web.HTTPPermanentRedirect("/", headers=HEADERS)

    story = session.story

    while story.presenter.frames:
        frame = story.presenter.frames.pop(0)
        animation = story.presenter.animate(
            frame,
            dwell=story.presenter.dwell,
            pause=story.presenter.pause
        )
        if animation:
            story.animation = animation
            break

    if story.context.get_state(Operation) == Operation.frames:
        refresh = Presenter.refresh_animations(story.animation, min_val=2)
        refresh_target = story.refresh_target("/{0.hex}".format(uid))
    else:
        refresh = None
        refresh_target = None

    title = next(iter(story.presenter.metadata.get("project", ["Tea and Sympathy"])), "Tea and Sympathy")
    controls = [
        "\n".join(story.render_action_form(action, autofocus=not n))
        for n, action in enumerate(story.actions)
        if story.context.get_state(Operation) not in (Operation.finish, Operation.frames)
    ]
    rv = story.render_body_html(title=title, next_=refresh_target, refresh=refresh).format(
        '<link rel="stylesheet" href="/css/theme/tas.css" />',
        story.render_dict_to_css(vars(story.settings)),
        story.render_animated_frame_to_html(story.animation, controls)
    )

    return web.Response(text=rv, content_type="text/html", headers=HEADERS)


async def post_command(request):
    uid = uuid.UUID(hex=request.match_info["session"])
    try:
        session = request.app["sessions"][uid]
    except KeyError:
        raise web.HTTPSeeOther("/", headers=HEADERS)

    story = session.story
    data = await request.post()
    cmd = data["cmd"]
    if cmd and not story.context.validator.match(cmd):
        raise web.HTTPUnauthorized(reason="User sent invalid command.")
    else:
        text = story.context.deliver(cmd, presenter=story.presenter)
        story.presenter = story.represent(text, facts=story.context.facts, previous=story.presenter)
    raise web.HTTPFound("/{0.hex}".format(uid))


def build_app(args):
    app = web.Application()
    app.add_routes([
        web.get("/", get_root),
        web.get("/metrics", get_metrics),
        web.get("/{{session:{0}}}".format(VALIDATION["session"].pattern), get_session),
        web.post("/{{session:{0}}}/cmd/".format(VALIDATION["session"].pattern), post_command),
    ])
    app.router.add_static(
        "/css/base/",
        pkg_resources.resource_filename("turberfield.catchphrase", "css")
    )
    app.router.add_static(
        "/css/theme/",
        pkg_resources.resource_filename("tas", "css")
    )
    app["sessions"] = {}
    app.on_startup.append(start_tasks)
    app.on_cleanup.append(cleanup_tasks)
    return app


def main(args):
    log = logging.getLogger(log_setup(args, ""))
    app = build_app(args)
    log.info("Serving on {0.host}:{0.port}".format(args))
    return web.run_app(app, host=args.host, port=args.port)


def parser(description=__doc__):
    rv = argparse.ArgumentParser(description)
    rv.add_argument(
        "--version", action="store_true", default=False,
        help="Print the current version number.")
    rv.add_argument(
        "-v", "--verbose", required=False,
        action="store_const", dest="log_level",
        const=logging.DEBUG, default=logging.INFO,
        help="Increase the verbosity of output.")
    rv.add_argument(
        "--log", default=None, dest="log_path",
        help="Set a file path for log output."
    )
    rv.add_argument(
        "--host", default="127.0.0.1",
        help="Set an interface on which to serve."
    )
    rv.add_argument(
        "--port", default=8080, type=int,
        help="Set a port on which to serve."
    )
    return rv


def run():
    p = parser()
    args = p.parse_args()

    rv = 0
    if args.version:
        sys.stdout.write(tas.__version__)
        sys.stdout.write("\n")
    else:
        rv = main(args)

    if rv == 2:
        sys.stderr.write("\n Missing command.\n\n")
        p.print_help()

    sys.exit(rv)


if __name__ == "__main__":
    run()
