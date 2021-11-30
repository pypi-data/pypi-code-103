#!/usr/bin/env python3


# jp: a SAT command line tool
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2013-2016 Adrien Cossa (souliane@mailoo.org)

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
from .constants import Const as C

__commands__ = ["Param"]


class Get(base.CommandBase):
    def __init__(self, host):
        super(Get, self).__init__(
            host, "get", need_connect=False, help=_("get a parameter value")
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "category", nargs="?", help=_("category of the parameter")
        )
        self.parser.add_argument("name", nargs="?", help=_("name of the parameter"))
        self.parser.add_argument(
            "-a",
            "--attribute",
            type=str,
            default="value",
            help=_("name of the attribute to get"),
        )
        self.parser.add_argument(
            "--security-limit", type=int, default=-1, help=_("security limit")
        )

    async def start(self):
        if self.args.category is None:
            categories = await self.host.bridge.getParamsCategories()
            print("\n".join(categories))
        elif self.args.name is None:
            try:
                values_dict = await self.host.bridge.asyncGetParamsValuesFromCategory(
                    self.args.category, self.args.security_limit, "", "", self.profile
                )
            except Exception as e:
                self.disp(
                    _("can't find requested parameters: {e}").format(e=e), error=True
                )
                self.host.quit(C.EXIT_NOT_FOUND)
            else:
                for name, value in values_dict.items():
                    print(f"{name}\t{value}")
        else:
            try:
                value = await self.host.bridge.asyncGetParamA(
                    self.args.name,
                    self.args.category,
                    self.args.attribute,
                    self.args.security_limit,
                    self.profile,
                )
            except Exception as e:
                self.disp(
                    _("can't find requested parameter: {e}").format(e=e), error=True
                )
                self.host.quit(C.EXIT_NOT_FOUND)
            else:
                print(value)
        self.host.quit()


class Set(base.CommandBase):
    def __init__(self, host):
        super(Set, self).__init__(
            host, "set", need_connect=False, help=_("set a parameter value")
        )

    def add_parser_options(self):
        self.parser.add_argument("category", help=_("category of the parameter"))
        self.parser.add_argument("name", help=_("name of the parameter"))
        self.parser.add_argument("value", help=_("name of the parameter"))
        self.parser.add_argument(
            "--security-limit", type=int, default=-1, help=_("security limit")
        )

    async def start(self):
        try:
            await self.host.bridge.setParam(
                self.args.name,
                self.args.value,
                self.args.category,
                self.args.security_limit,
                self.profile,
            )
        except Exception as e:
            self.disp(_("can't set requested parameter: {e}").format(e=e), error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.host.quit()


class SaveTemplate(base.CommandBase):
    # FIXME: this should probably be removed, it's not used and not useful for end-user

    def __init__(self, host):
        super(SaveTemplate, self).__init__(
            host,
            "save",
            use_profile=False,
            help=_("save parameters template to xml file"),
        )

    def add_parser_options(self):
        self.parser.add_argument("filename", type=str, help=_("output file"))

    async def start(self):
        """Save parameters template to XML file"""
        try:
            await self.host.bridge.saveParamsTemplate(self.args.filename)
        except Exception as e:
            self.disp(_("can't save parameters to file: {e}").format(e=e), error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(
                _("parameters saved to file {filename}").format(
                    filename=self.args.filename
                )
            )
            self.host.quit()


class LoadTemplate(base.CommandBase):
    # FIXME: this should probably be removed, it's not used and not useful for end-user

    def __init__(self, host):
        super(LoadTemplate, self).__init__(
            host,
            "load",
            use_profile=False,
            help=_("load parameters template from xml file"),
        )

    def add_parser_options(self):
        self.parser.add_argument("filename", type=str, help=_("input file"))

    async def start(self):
        """Load parameters template from xml file"""
        try:
            self.host.bridge.loadParamsTemplate(self.args.filename)
        except Exception as e:
            self.disp(_("can't load parameters from file: {e}").format(e=e), error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(
                _("parameters loaded from file {filename}").format(
                    filename=self.args.filename
                )
            )
            self.host.quit()


class Param(base.CommandBase):
    subcommands = (Get, Set, SaveTemplate, LoadTemplate)

    def __init__(self, host):
        super(Param, self).__init__(
            host, "param", use_profile=False, help=_("Save/load parameters template")
        )
