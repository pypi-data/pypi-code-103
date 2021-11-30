#!/usr/bin/env python3


# jp: a SàT command line tool
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import subprocess
import argparse
import sys
import shlex
import asyncio
from . import base
from sat.core.i18n import _
from sat.core import exceptions
from sat_frontends.jp.constants import Const as C
from sat.tools.common.ansi import ANSI as A

__commands__ = ["Input"]
OPT_STDIN = "stdin"
OPT_SHORT = "short"
OPT_LONG = "long"
OPT_POS = "positional"
OPT_IGNORE = "ignore"
OPT_TYPES = (OPT_STDIN, OPT_SHORT, OPT_LONG, OPT_POS, OPT_IGNORE)
OPT_EMPTY_SKIP = "skip"
OPT_EMPTY_IGNORE = "ignore"
OPT_EMPTY_CHOICES = (OPT_EMPTY_SKIP, OPT_EMPTY_IGNORE)


class InputCommon(base.CommandBase):
    def __init__(self, host, name, help):
        base.CommandBase.__init__(
            self, host, name, use_verbose=True, use_profile=False, help=help
        )
        self.idx = 0
        self.reset()

    def reset(self):
        self.args_idx = 0
        self._stdin = []
        self._opts = []
        self._pos = []
        self._values_ori = []

    def add_parser_options(self):
        self.parser.add_argument(
            "--encoding", default="utf-8", help=_("encoding of the input data")
        )
        self.parser.add_argument(
            "-i",
            "--stdin",
            action="append_const",
            const=(OPT_STDIN, None),
            dest="arguments",
            help=_("standard input"),
        )
        self.parser.add_argument(
            "-s",
            "--short",
            type=self.opt(OPT_SHORT),
            action="append",
            dest="arguments",
            help=_("short option"),
        )
        self.parser.add_argument(
            "-l",
            "--long",
            type=self.opt(OPT_LONG),
            action="append",
            dest="arguments",
            help=_("long option"),
        )
        self.parser.add_argument(
            "-p",
            "--positional",
            type=self.opt(OPT_POS),
            action="append",
            dest="arguments",
            help=_("positional argument"),
        )
        self.parser.add_argument(
            "-x",
            "--ignore",
            action="append_const",
            const=(OPT_IGNORE, None),
            dest="arguments",
            help=_("ignore value"),
        )
        self.parser.add_argument(
            "-D",
            "--debug",
            action="store_true",
            help=_("don't actually run commands but echo what would be launched"),
        )
        self.parser.add_argument(
            "--log", type=argparse.FileType("w"), help=_("log stdout to FILE")
        )
        self.parser.add_argument(
            "--log-err", type=argparse.FileType("w"), help=_("log stderr to FILE")
        )
        self.parser.add_argument("command", nargs=argparse.REMAINDER)

    def opt(self, type_):
        return lambda s: (type_, s)

    def addValue(self, value):
        """add a parsed value according to arguments sequence"""
        self._values_ori.append(value)
        arguments = self.args.arguments
        try:
            arg_type, arg_name = arguments[self.args_idx]
        except IndexError:
            self.disp(
                _("arguments in input data and in arguments sequence don't match"),
                error=True,
            )
            self.host.quit(C.EXIT_DATA_ERROR)
        self.args_idx += 1
        while self.args_idx < len(arguments):
            next_arg = arguments[self.args_idx]
            if next_arg[0] not in OPT_TYPES:
                # value will not be used if False or None, so we skip filter
                if value not in (False, None):
                    # we have a filter
                    filter_type, filter_arg = arguments[self.args_idx]
                    value = self.filter(filter_type, filter_arg, value)
            else:
                break
            self.args_idx += 1

        if value is None:
            # we ignore this argument
            return

        if value is False:
            # we skip the whole row
            if self.args.debug:
                self.disp(
                    A.color(
                        C.A_SUBHEADER,
                        _("values: "),
                        A.RESET,
                        ", ".join(self._values_ori),
                    ),
                    2,
                )
                self.disp(A.color(A.BOLD, _("**SKIPPING**\n")))
            self.reset()
            self.idx += 1
            raise exceptions.CancelError

        if not isinstance(value, list):
            value = [value]

        for v in value:
            if arg_type == OPT_STDIN:
                self._stdin.append(v)
            elif arg_type == OPT_SHORT:
                self._opts.append("-{}".format(arg_name))
                self._opts.append(v)
            elif arg_type == OPT_LONG:
                self._opts.append("--{}".format(arg_name))
                self._opts.append(v)
            elif arg_type == OPT_POS:
                self._pos.append(v)
            elif arg_type == OPT_IGNORE:
                pass
            else:
                self.parser.error(
                    _(
                        "Invalid argument, an option type is expected, got {type_}:{name}"
                    ).format(type_=arg_type, name=arg_name)
                )

    async def runCommand(self):
        """run requested command with parsed arguments"""
        if self.args_idx != len(self.args.arguments):
            self.disp(
                _("arguments in input data and in arguments sequence don't match"),
                error=True,
            )
            self.host.quit(C.EXIT_DATA_ERROR)
        end = '\n' if self.args.debug else ' '
        self.disp(
            A.color(C.A_HEADER, _("command {idx}").format(idx=self.idx)),
            end = end,
        )
        stdin = "".join(self._stdin)
        if self.args.debug:
            self.disp(
                A.color(
                    C.A_SUBHEADER,
                    _("values: "),
                    A.RESET,
                    ", ".join([shlex.quote(a) for a in self._values_ori])
                ),
                2,
            )

            if stdin:
                self.disp(A.color(C.A_SUBHEADER, "--- STDIN ---"))
                self.disp(stdin)
                self.disp(A.color(C.A_SUBHEADER, "-------------"))

            self.disp(
                "{indent}{prog} {static} {options} {positionals}".format(
                    indent=4 * " ",
                    prog=sys.argv[0],
                    static=" ".join(self.args.command),
                    options=" ".join(shlex.quote(o) for o in self._opts),
                    positionals=" ".join(shlex.quote(p) for p in self._pos),
                )
            )
            self.disp("\n")
        else:
            self.disp(" (" + ", ".join(self._values_ori) + ")", 2, end=' ')
            args = [sys.argv[0]] + self.args.command + self._opts + self._pos
            p = await asyncio.create_subprocess_exec(
                *args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = await p.communicate(stdin.encode('utf-8'))
            log = self.args.log
            log_err = self.args.log_err
            log_tpl = "{command}\n{buff}\n\n"
            if log:
                log.write(log_tpl.format(
                    command=" ".join(shlex.quote(a) for a in args),
                    buff=stdout.decode('utf-8', 'replace')))
            if log_err:
                log_err.write(log_tpl.format(
                    command=" ".join(shlex.quote(a) for a in args),
                    buff=stderr.decode('utf-8', 'replace')))
            ret = p.returncode
            if ret == 0:
                self.disp(A.color(C.A_SUCCESS, _("OK")))
            else:
                self.disp(A.color(C.A_FAILURE, _("FAILED")))

        self.reset()
        self.idx += 1

    def filter(self, filter_type, filter_arg, value):
        """change input value

        @param filter_type(unicode): name of the filter
        @param filter_arg(unicode, None): argument of the filter
        @param value(unicode): value to filter
        @return (unicode, False, None): modified value
            False to skip the whole row
            None to ignore this argument (but continue row with other ones)
        """
        raise NotImplementedError


class Csv(InputCommon):
    def __init__(self, host):
        super(Csv, self).__init__(host, "csv", _("comma-separated values"))

    def add_parser_options(self):
        InputCommon.add_parser_options(self)
        self.parser.add_argument(
            "-r",
            "--row",
            type=int,
            default=0,
            help=_("starting row (previous ones will be ignored)"),
        )
        self.parser.add_argument(
            "-S",
            "--split",
            action="append_const",
            const=("split", None),
            dest="arguments",
            help=_("split value in several options"),
        )
        self.parser.add_argument(
            "-E",
            "--empty",
            action="append",
            type=self.opt("empty"),
            dest="arguments",
            help=_("action to do on empty value ({choices})").format(
                choices=", ".join(OPT_EMPTY_CHOICES)
            ),
        )

    def filter(self, filter_type, filter_arg, value):
        if filter_type == "split":
            return value.split()
        elif filter_type == "empty":
            if filter_arg == OPT_EMPTY_IGNORE:
                return value if value else None
            elif filter_arg == OPT_EMPTY_SKIP:
                return value if value else False
            else:
                self.parser.error(
                    _("--empty value must be one of {choices}").format(
                        choices=", ".join(OPT_EMPTY_CHOICES)
                    )
                )

        super(Csv, self).filter(filter_type, filter_arg, value)

    async def start(self):
        import csv

        if self.args.encoding:
            sys.stdin.reconfigure(encoding=self.args.encoding, errors="replace")
        reader = csv.reader(sys.stdin)
        for idx, row in enumerate(reader):
            try:
                if idx < self.args.row:
                    continue
                for value in row:
                    self.addValue(value)
                await self.runCommand()
            except exceptions.CancelError:
                #  this row has been cancelled, we skip it
                continue

        self.host.quit()


class Input(base.CommandBase):
    subcommands = (Csv,)

    def __init__(self, host):
        super(Input, self).__init__(
            host,
            "input",
            use_profile=False,
            help=_("launch command with external input"),
        )
