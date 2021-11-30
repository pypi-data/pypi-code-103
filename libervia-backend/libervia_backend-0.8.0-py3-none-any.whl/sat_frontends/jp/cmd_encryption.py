#!/usr/bin/env python3


# jp: a SAT command line tool
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

from sat_frontends.jp import base
from sat_frontends.jp.constants import Const as C
from sat.core.i18n import _
from sat.tools.common import data_format
from sat_frontends.jp import xmlui_manager

__commands__ = ["Encryption"]


class EncryptionAlgorithms(base.CommandBase):

    def __init__(self, host):
        extra_outputs = {"default": self.default_output}
        super(EncryptionAlgorithms, self).__init__(
            host, "algorithms",
            use_output=C.OUTPUT_LIST_DICT,
            extra_outputs=extra_outputs,
            use_profile=False,
            help=_("show available encryption algorithms"))

    def add_parser_options(self):
        pass

    def default_output(self, plugins):
        if not plugins:
            self.disp(_("No encryption plugin registered!"))
        else:
            self.disp(_("Following encryption algorithms are available: {algos}").format(
                algos=', '.join([p['name'] for p in plugins])))

    async def start(self):
        try:
            plugins_ser = await self.host.bridge.encryptionPluginsGet()
            plugins = data_format.deserialise(plugins_ser, type_check=list)
        except Exception as e:
            self.disp(f"can't retrieve plugins: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            await self.output(plugins)
            self.host.quit()


class EncryptionGet(base.CommandBase):

    def __init__(self, host):
        super(EncryptionGet, self).__init__(
            host, "get",
            use_output=C.OUTPUT_DICT,
            help=_("get encryption session data"))

    def add_parser_options(self):
        self.parser.add_argument(
            "jid",
            help=_("jid of the entity to check")
        )

    async def start(self):
        jids = await self.host.check_jids([self.args.jid])
        jid = jids[0]
        try:
            serialised = await self.host.bridge.messageEncryptionGet(jid, self.profile)
        except Exception as e:
            self.disp(f"can't get session: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        session_data = data_format.deserialise(serialised)
        if session_data is None:
            self.disp(
                "No encryption session found, the messages are sent in plain text.")
            self.host.quit(C.EXIT_NOT_FOUND)
        await self.output(session_data)
        self.host.quit()


class EncryptionStart(base.CommandBase):

    def __init__(self, host):
        super(EncryptionStart, self).__init__(
            host, "start",
            help=_("start encrypted session with an entity"))

    def add_parser_options(self):
        self.parser.add_argument(
            "--encrypt-noreplace",
            action="store_true",
            help=_("don't replace encryption algorithm if an other one is already used"))
        algorithm = self.parser.add_mutually_exclusive_group()
        algorithm.add_argument(
            "-n", "--name", help=_("algorithm name (DEFAULT: choose automatically)"))
        algorithm.add_argument(
            "-N", "--namespace",
            help=_("algorithm namespace (DEFAULT: choose automatically)"))
        self.parser.add_argument(
            "jid",
            help=_("jid of the entity to stop encrypted session with")
        )

    async def start(self):
        if self.args.name is not None:
            try:
                namespace = await self.host.bridge.encryptionNamespaceGet(self.args.name)
            except Exception as e:
                self.disp(f"can't get encryption namespace: {e}", error=True)
                self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        elif self.args.namespace is not None:
            namespace = self.args.namespace
        else:
            namespace = ""

        jids = await self.host.check_jids([self.args.jid])
        jid = jids[0]

        try:
            await self.host.bridge.messageEncryptionStart(
                jid, namespace, not self.args.encrypt_noreplace,
                self.profile)
        except Exception as e:
            self.disp(f"can't get encryption namespace: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        self.host.quit()


class EncryptionStop(base.CommandBase):

    def __init__(self, host):
        super(EncryptionStop, self).__init__(
            host, "stop",
            help=_("stop encrypted session with an entity"))

    def add_parser_options(self):
        self.parser.add_argument(
            "jid",
            help=_("jid of the entity to stop encrypted session with")
        )

    async def start(self):
        jids = await self.host.check_jids([self.args.jid])
        jid = jids[0]
        try:
            await self.host.bridge.messageEncryptionStop(jid, self.profile)
        except Exception as e:
            self.disp(f"can't end encrypted session: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        self.host.quit()


class TrustUI(base.CommandBase):

    def __init__(self, host):
        super(TrustUI, self).__init__(
            host, "ui",
            help=_("get UI to manage trust"))

    def add_parser_options(self):
        self.parser.add_argument(
            "jid",
            help=_("jid of the entity to stop encrypted session with")
        )
        algorithm = self.parser.add_mutually_exclusive_group()
        algorithm.add_argument(
            "-n", "--name", help=_("algorithm name (DEFAULT: current algorithm)"))
        algorithm.add_argument(
            "-N", "--namespace",
            help=_("algorithm namespace (DEFAULT: current algorithm)"))

    async def start(self):
        if self.args.name is not None:
            try:
                namespace = await self.host.bridge.encryptionNamespaceGet(self.args.name)
            except Exception as e:
                self.disp(f"can't get encryption namespace: {e}", error=True)
                self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        elif self.args.namespace is not None:
            namespace = self.args.namespace
        else:
            namespace = ""

        jids = await self.host.check_jids([self.args.jid])
        jid = jids[0]

        try:
            xmlui_raw = await self.host.bridge.encryptionTrustUIGet(
                jid, namespace, self.profile)
        except Exception as e:
            self.disp(f"can't get encryption session trust UI: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        xmlui = xmlui_manager.create(self.host, xmlui_raw)
        await xmlui.show()
        if xmlui.type != C.XMLUI_DIALOG:
            await xmlui.submitForm()
        self.host.quit()

class EncryptionTrust(base.CommandBase):
    subcommands = (TrustUI,)

    def __init__(self, host):
        super(EncryptionTrust, self).__init__(
            host, "trust", use_profile=False, help=_("trust manangement")
        )


class Encryption(base.CommandBase):
    subcommands = (EncryptionAlgorithms, EncryptionGet, EncryptionStart, EncryptionStop,
                   EncryptionTrust)

    def __init__(self, host):
        super(Encryption, self).__init__(
            host, "encryption", use_profile=False, help=_("encryption sessions handling")
        )
