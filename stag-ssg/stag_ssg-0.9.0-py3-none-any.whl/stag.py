# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2021 Michał Góral.

import os
import sys
import argparse
import shutil
import logging
import pkgutil
import signal
from copy import deepcopy

from stag import __version__ as _version
from stag.config import read_config
from stag.ecs import Path, Page
from stag.site import Site
from stag.writing import render
from stag.server import serve_until_changed

log = logging.getLogger(__name__)


def load_plugins_from(paths, disabled, *register_args):
    for finder, name, ispkg in pkgutil.iter_modules(paths):
        if name.startswith("_"):
            continue

        if name in disabled:
            continue

        found = finder.find_module(name)
        if found:
            mod = found.load_module()
            try:
                mod.register_plugin(*register_args)
                log.debug(f"Plugin loaded: {name}")
            except AttributeError as e:
                log.error(f"{e} - plugin will be disabled")


def load_plugins(site):
    search_paths = [
        os.path.join(os.path.dirname(__file__), "plugins"),
        site.config.plugins_path,
    ]

    disabled = site.config.plugins_disabled

    load_plugins_from(search_paths, disabled, site)
    site.signals.plugins_loaded.emit()


def build(site):
    config = site.config

    if not os.path.isdir(config.content):
        raise IOError(
            f'Not a directory: "{config.content}" (Are you inside a correct directory? Is config.content correct?).'
        )

    log.info(f"Building site to {config.output}")

    roots = [
        config.content,
        os.path.join(config.template.name, "static"),
        "static",
    ]

    site.signals.readers_init.emit(site)

    for root in roots:
        gather_files(root, site)

    site.signals.readers_finished.emit(site)

    site.signals.processors_init.emit(site)
    site.signals.processors_finished.emit(site)

    site.signals.rendering_init.emit(site)
    shutil.rmtree(config.output, ignore_errors=True)
    os.makedirs(config.output)
    render(site)
    site.signals.rendering_finished.emit(site)

    site.signals.site_finished.emit(site)


def build_cmd(args):
    config = read_config(args.config)
    override_config_with_commandline_args(config, args)

    site = Site(config=config)
    load_plugins(site)
    build(site)


def serve_cmd(args):
    config = read_config(args.config)
    override_config_with_commandline_args(config, args)

    def _exit(sig, frame):
        sys.exit(sig)

    signal.signal(signal.SIGINT, _exit)
    signal.signal(signal.SIGTERM, _exit)

    changes = 0
    while True:
        site = Site(config=config)
        load_plugins(site)

        try:
            build(site)
        except Exception as e:
            log.error(e)
            log.error("Building of site failed. You may still have the old version!")
            if args.verbosity == logging.DEBUG:
                raise
            if changes == 0:
                return

        templ = (os.path.join(config.template.name, "static"),)
        patterns = (
            "config.toml",
            f"{config.content}/**/*",
            f"{config.content}/**/.*",
            f"{templ}/*",
            f"{templ}/static/**/*",
            "static/**/*",
            config.output,
        )

        try:
            serve_until_changed(config.output, args.port, patterns)
        except Exception as e:
            log.error(e)
            log.error("Critical error detected while running HTTP server.")
            return

        log.info("")
        log.info("Change detected, regenerating.")
        changes += 1


def gather_files(srcdir, site):
    for curdir, _, files in os.walk(srcdir):
        for f in files:
            path = Path(os.path.join(curdir, f), srcdir)
            relurl = site.readers.get_path(path)
            site.make_page(relurl, source=path)


def override_config_with_commandline_args(config, args):
    for name, val in args.__dict__.items():
        if val is not None and hasattr(config, name):
            setattr(config, name, args.__dict__[name])


def prepare_args(argv):
    parser = argparse.ArgumentParser(description="Simply Stupid Static Site Generator")
    parser.set_defaults(verbosity=logging.INFO)

    parser.add_argument(
        "-c",
        "--config",
        nargs="?",
        default="config.toml",
        help="path to stag's configuration file",
    )

    parser.add_argument(
        "-C",
        "--change-directory",
        metavar="DIR",
        help="run as if stag was started in DIR instead of current working directory",
    )

    parser.add_argument(
        "-D",
        "--debug",
        action="store_const",
        const=logging.DEBUG,
        dest="verbosity",
        help="show debug messages",
    )

    parser.add_argument("--version", action="version", version=f"%(prog)s {_version}")

    sp = parser.add_subparsers(required=True, dest="subcommands")

    sp_build = sp.add_parser("build")
    sp_build.add_argument("-o", "--output", help="output directory")
    sp_build.set_defaults(func=build_cmd)

    sp_serve = sp.add_parser("serve")
    sp_serve.add_argument("-o", "--output", help="output directory")
    sp_serve.add_argument("-p", "--port", type=int, default="8000", help="HTTP port")
    sp_serve.set_defaults(func=serve_cmd)

    return parser.parse_args(argv)


def main_(argv):
    args = prepare_args(argv)
    logging.basicConfig(format="%(message)s", level=args.verbosity)

    try:
        if args.change_directory:
            os.chdir(args.change_directory)

        return args.func(args)
    except Exception as e:
        log.error(f"Critical error: {e}")
        if args.verbosity == logging.DEBUG:
            import pdb, traceback

            extype, value, tb = sys.exc_info()
            traceback.print_exc()
            pdb.post_mortem(tb)
            raise
        return 1


def main():
    return main_(sys.argv[1:])
