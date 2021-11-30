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


from . import base
from sat.core.i18n import _
from sat_frontends.jp.constants import Const as C
from sat.tools.common.ansi import ANSI as A
import json

__commands__ = ["Debug"]


class BridgeCommon(object):
    def evalArgs(self):
        if self.args.arg:
            try:
                return eval("[{}]".format(",".join(self.args.arg)))
            except SyntaxError as e:
                self.disp(
                    "Can't evaluate arguments: {mess}\n{text}\n{offset}^".format(
                        mess=e, text=e.text, offset=" " * (e.offset - 1)
                    ),
                    error=True,
                )
                self.host.quit(C.EXIT_BAD_ARG)
        else:
            return []


class Method(base.CommandBase, BridgeCommon):
    def __init__(self, host):
        base.CommandBase.__init__(self, host, "method", help=_("call a bridge method"))
        BridgeCommon.__init__(self)

    def add_parser_options(self):
        self.parser.add_argument(
            "method", type=str, help=_("name of the method to execute")
        )
        self.parser.add_argument("arg", nargs="*", help=_("argument of the method"))

    async def start(self):
        method = getattr(self.host.bridge, self.args.method)
        import inspect

        argspec = inspect.getargspec(method)

        kwargs = {}
        if "profile_key" in argspec.args:
            kwargs["profile_key"] = self.profile
        elif "profile" in argspec.args:
            kwargs["profile"] = self.profile

        args = self.evalArgs()

        try:
            ret = await method(
                *args,
                **kwargs,
            )
        except Exception as e:
            self.disp(
                _("Error while executing {method}: {e}").format(
                    method=self.args.method, e=e
                ),
                error=True,
            )
            self.host.quit(C.EXIT_ERROR)
        else:
            if ret is not None:
                self.disp(str(ret))
            self.host.quit()


class Signal(base.CommandBase, BridgeCommon):
    def __init__(self, host):
        base.CommandBase.__init__(
            self, host, "signal", help=_("send a fake signal from backend")
        )
        BridgeCommon.__init__(self)

    def add_parser_options(self):
        self.parser.add_argument("signal", type=str, help=_("name of the signal to send"))
        self.parser.add_argument("arg", nargs="*", help=_("argument of the signal"))

    async def start(self):
        args = self.evalArgs()
        json_args = json.dumps(args)
        # XXX: we use self.args.profile and not self.profile
        #      because we want the raw profile_key (so plugin handle C.PROF_KEY_NONE)
        try:
            await self.host.bridge.debugFakeSignal(
                self.args.signal, json_args, self.args.profile
            )
        except Exception as e:
            self.disp(_("Can't send fake signal: {e}").format(e=e), error=True)
            self.host.quit(C.EXIT_ERROR)
        else:
            self.host.quit()


class Bridge(base.CommandBase):
    subcommands = (Method, Signal)

    def __init__(self, host):
        super(Bridge, self).__init__(
            host, "bridge", use_profile=False, help=_("bridge s(t)imulation")
        )


class Monitor(base.CommandBase):
    def __init__(self, host):
        super(Monitor, self).__init__(
            host,
            "monitor",
            use_verbose=True,
            use_profile=False,
            use_output=C.OUTPUT_XML,
            help=_("monitor XML stream"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-d",
            "--direction",
            choices=("in", "out", "both"),
            default="both",
            help=_("stream direction filter"),
        )

    async def printXML(self, direction, xml_data, profile):
        if self.args.direction == "in" and direction != "IN":
            return
        if self.args.direction == "out" and direction != "OUT":
            return
        verbosity = self.host.verbosity
        if not xml_data.strip():
            if verbosity <= 2:
                return
            whiteping = True
        else:
            whiteping = False

        if verbosity:
            profile_disp = f" ({profile})" if verbosity > 1 else ""
            if direction == "IN":
                self.disp(
                    A.color(
                        A.BOLD, A.FG_YELLOW, "<<<===== IN ====", A.FG_WHITE, profile_disp
                    )
                )
            else:
                self.disp(
                    A.color(
                        A.BOLD, A.FG_CYAN, "==== OUT ====>>>", A.FG_WHITE, profile_disp
                    )
                )
        if whiteping:
            self.disp("[WHITESPACE PING]")
        else:
            try:
                await self.output(xml_data)
            except Exception:
                #  initial stream is not valid XML,
                # in this case we print directly to data
                #  FIXME: we should test directly lxml.etree.XMLSyntaxError
                #        but importing lxml directly here is not clean
                #        should be wrapped in a custom Exception
                self.disp(xml_data)
                self.disp("")

    async def start(self):
        self.host.bridge.register_signal("xmlLog", self.printXML, "plugin")


class Theme(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self, host, "theme", help=_("print colours used with your background")
        )

    def add_parser_options(self):
        pass

    async def start(self):
        print(f"background currently used: {A.BOLD}{self.host.background}{A.RESET}\n")
        for attr in dir(C):
            if not attr.startswith("A_"):
                continue
            color = getattr(C, attr)
            if attr == "A_LEVEL_COLORS":
                # This constant contains multiple colors
                self.disp("LEVEL COLORS: ", end=" ")
                for idx, c in enumerate(color):
                    last = idx == len(color) - 1
                    end = "\n" if last else " "
                    self.disp(
                        c + f"LEVEL_{idx}" + A.RESET + (", " if not last else ""), end=end
                    )
            else:
                text = attr[2:]
                self.disp(A.color(color, text))
        self.host.quit()


class Debug(base.CommandBase):
    subcommands = (Bridge, Monitor, Theme)

    def __init__(self, host):
        super(Debug, self).__init__(
            host, "debug", use_profile=False, help=_("debugging tools")
        )
