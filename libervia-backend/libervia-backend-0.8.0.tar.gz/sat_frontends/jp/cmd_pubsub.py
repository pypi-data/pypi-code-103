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


import argparse
import os.path
import re
import sys
import subprocess
import asyncio
from . import base
from sat.core.i18n import _
from sat.core import exceptions
from sat_frontends.jp.constants import Const as C
from sat_frontends.jp import common
from sat_frontends.jp import arg_tools
from sat_frontends.jp import xml_tools
from functools import partial
from sat.tools.common import data_format
from sat.tools.common import uri
from sat.tools.common.ansi import ANSI as A
from sat_frontends.tools import jid, strings
from sat_frontends.bridge.bridge_frontend import BridgeException

__commands__ = ["Pubsub"]

PUBSUB_TMP_DIR = "pubsub"
PUBSUB_SCHEMA_TMP_DIR = PUBSUB_TMP_DIR + "_schema"
ALLOWED_SUBSCRIPTIONS_OWNER = ("subscribed", "pending", "none")

# TODO: need to split this class in several modules, plugin should handle subcommands


class NodeInfo(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "info",
            use_output=C.OUTPUT_DICT,
            use_pubsub=True,
            pubsub_flags={C.NODE},
            help=_("retrieve node configuration"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-k",
            "--key",
            action="append",
            dest="keys",
            help=_("data key to filter"),
        )

    def removePrefix(self, key):
        return key[7:] if key.startswith("pubsub#") else key

    def filterKey(self, key):
        return any((key == k or key == "pubsub#" + k) for k in self.args.keys)

    async def start(self):
        try:
            config_dict = await self.host.bridge.psNodeConfigurationGet(
                self.args.service,
                self.args.node,
                self.profile,
            )
        except BridgeException as e:
            if e.condition == "item-not-found":
                self.disp(
                    f"The node {self.args.node} doesn't exist on {self.args.service}",
                    error=True,
                )
                self.host.quit(C.EXIT_NOT_FOUND)
            else:
                self.disp(f"can't get node configuration: {e}", error=True)
                self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        except Exception as e:
            self.disp(f"Internal error: {e}", error=True)
            self.host.quit(C.EXIT_INTERNAL_ERROR)
        else:
            key_filter = (lambda k: True) if not self.args.keys else self.filterKey
            config_dict = {
                self.removePrefix(k): v for k, v in config_dict.items() if key_filter(k)
            }
            await self.output(config_dict)
            self.host.quit()


class NodeCreate(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "create",
            use_output=C.OUTPUT_DICT,
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_verbose=True,
            help=_("create a node"),
        )

    @staticmethod
    def add_node_config_options(parser):
        parser.add_argument(
            "-f",
            "--field",
            action="append",
            nargs=2,
            dest="fields",
            default=[],
            metavar=("KEY", "VALUE"),
            help=_("configuration field to set"),
        )
        parser.add_argument(
            "-F",
            "--full-prefix",
            action="store_true",
            help=_('don\'t prepend "pubsub#" prefix to field names'),
        )

    def add_parser_options(self):
        self.add_node_config_options(self.parser)

    @staticmethod
    def get_config_options(args):
        if not args.full_prefix:
            return {"pubsub#" + k: v for k, v in args.fields}
        else:
            return dict(args.fields)

    async def start(self):
        options = self.get_config_options(self.args)
        try:
            node_id = await self.host.bridge.psNodeCreate(
                self.args.service,
                self.args.node,
                options,
                self.profile,
            )
        except Exception as e:
            self.disp(msg=_("can't create node: {e}").format(e=e), error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            if self.host.verbosity:
                announce = _("node created successfully: ")
            else:
                announce = ""
            self.disp(announce + node_id)
            self.host.quit()


class NodePurge(base.CommandBase):
    def __init__(self, host):
        super(NodePurge, self).__init__(
            host,
            "purge",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            help=_("purge a node (i.e. remove all items from it)"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help=_("purge node without confirmation"),
        )

    async def start(self):
        if not self.args.force:
            if not self.args.service:
                message = _(
                    "Are you sure to purge PEP node [{node}]? This will "
                    "delete ALL items from it!"
                ).format(node=self.args.node)
            else:
                message = _(
                    "Are you sure to delete node [{node}] on service "
                    "[{service}]? This will delete ALL items from it!"
                ).format(node=self.args.node, service=self.args.service)
            await self.host.confirmOrQuit(message, _("node purge cancelled"))

        try:
            await self.host.bridge.psNodePurge(
                self.args.service,
                self.args.node,
                self.profile,
            )
        except Exception as e:
            self.disp(msg=_("can't purge node: {e}").format(e=e), error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(_("node [{node}] purged successfully").format(node=self.args.node))
            self.host.quit()


class NodeDelete(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "delete",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            help=_("delete a node"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help=_("delete node without confirmation"),
        )

    async def start(self):
        if not self.args.force:
            if not self.args.service:
                message = _("Are you sure to delete PEP node [{node}] ?").format(
                    node=self.args.node
                )
            else:
                message = _(
                    "Are you sure to delete node [{node}] on " "service [{service}]?"
                ).format(node=self.args.node, service=self.args.service)
            await self.host.confirmOrQuit(message, _("node deletion cancelled"))

        try:
            await self.host.bridge.psNodeDelete(
                self.args.service,
                self.args.node,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't delete node: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(_("node [{node}] deleted successfully").format(node=self.args.node))
            self.host.quit()


class NodeSet(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "set",
            use_output=C.OUTPUT_DICT,
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_verbose=True,
            help=_("set node configuration"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-f",
            "--field",
            action="append",
            nargs=2,
            dest="fields",
            required=True,
            metavar=("KEY", "VALUE"),
            help=_("configuration field to set (required)"),
        )
        self.parser.add_argument(
            "-F",
            "--full-prefix",
            action="store_true",
            help=_('don\'t prepend "pubsub#" prefix to field names'),
        )

    def getKeyName(self, k):
        if self.args.full_prefix or k.startswith("pubsub#"):
            return k
        else:
            return "pubsub#" + k

    async def start(self):
        try:
            await self.host.bridge.psNodeConfigurationSet(
                self.args.service,
                self.args.node,
                {self.getKeyName(k): v for k, v in self.args.fields},
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't set node configuration: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(_("node configuration successful"), 1)
            self.host.quit()


class NodeImport(base.CommandBase):
    def __init__(self, host):
        super(NodeImport, self).__init__(
            host,
            "import",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            help=_("import raw XML to a node"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "--admin",
            action="store_true",
            help=_("do a pubsub admin request, needed to change publisher"),
        )
        self.parser.add_argument(
            "import_file",
            type=argparse.FileType(),
            help=_(
                "path to the XML file with data to import. The file must contain "
                "whole XML of each item to import."
            ),
        )

    async def start(self):
        try:
            element, etree = xml_tools.etreeParse(
                self, self.args.import_file, reraise=True
            )
        except Exception as e:
            from lxml.etree import XMLSyntaxError

            if isinstance(e, XMLSyntaxError) and e.code == 5:
                # we have extra content, this probaby means that item are not wrapped
                # so we wrap them here and try again
                self.args.import_file.seek(0)
                xml_buf = "<import>" + self.args.import_file.read() + "</import>"
                element, etree = xml_tools.etreeParse(self, xml_buf)

                # we reverse element as we expect to have most recently published element first
                # TODO: make this more explicit and add an option
        element[:] = reversed(element)

        if not all([i.tag == "{http://jabber.org/protocol/pubsub}item" for i in element]):
            self.disp(
                _("You are not using list of pubsub items, we can't import this file"),
                error=True,
            )
            self.host.quit(C.EXIT_DATA_ERROR)
            return

        items = [etree.tostring(i, encoding="unicode") for i in element]
        if self.args.admin:
            method = self.host.bridge.psAdminItemsSend
        else:
            self.disp(
                _(
                    "Items are imported without using admin mode, publisher can't "
                    "be changed"
                )
            )
            method = self.host.bridge.psItemsSend

        try:
            items_ids = await method(
                self.args.service,
                self.args.node,
                items,
                "",
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't send items: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            if items_ids:
                self.disp(
                    _("items published with id(s) {items_ids}").format(
                        items_ids=", ".join(items_ids)
                    )
                )
            else:
                self.disp(_("items published"))
            self.host.quit()


class NodeAffiliationsGet(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_output=C.OUTPUT_DICT,
            use_pubsub=True,
            pubsub_flags={C.NODE},
            help=_("retrieve node affiliations (for node owner)"),
        )

    def add_parser_options(self):
        pass

    async def start(self):
        try:
            affiliations = await self.host.bridge.psNodeAffiliationsGet(
                self.args.service,
                self.args.node,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't get node affiliations: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            await self.output(affiliations)
            self.host.quit()


class NodeAffiliationsSet(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "set",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_verbose=True,
            help=_("set affiliations (for node owner)"),
        )

    def add_parser_options(self):
        # XXX: we use optional argument syntax for a required one because list of list of 2 elements
        #      (used to construct dicts) don't work with positional arguments
        self.parser.add_argument(
            "-a",
            "--affiliation",
            dest="affiliations",
            metavar=("JID", "AFFILIATION"),
            required=True,
            action="append",
            nargs=2,
            help=_("entity/affiliation couple(s)"),
        )

    async def start(self):
        affiliations = dict(self.args.affiliations)
        try:
            await self.host.bridge.psNodeAffiliationsSet(
                self.args.service,
                self.args.node,
                affiliations,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't set node affiliations: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(_("affiliations have been set"), 1)
            self.host.quit()


class NodeAffiliations(base.CommandBase):
    subcommands = (NodeAffiliationsGet, NodeAffiliationsSet)

    def __init__(self, host):
        super(NodeAffiliations, self).__init__(
            host,
            "affiliations",
            use_profile=False,
            help=_("set or retrieve node affiliations"),
        )


class NodeSubscriptionsGet(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_output=C.OUTPUT_DICT,
            use_pubsub=True,
            pubsub_flags={C.NODE},
            help=_("retrieve node subscriptions (for node owner)"),
        )

    def add_parser_options(self):
        pass

    async def start(self):
        try:
            subscriptions = await self.host.bridge.psNodeSubscriptionsGet(
                self.args.service,
                self.args.node,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't get node subscriptions: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            await self.output(subscriptions)
            self.host.quit()


class StoreSubscriptionAction(argparse.Action):
    """Action which handle subscription parameter for owner

    list is given by pairs: jid and subscription state
    if subscription state is not specified, it default to "subscribed"
    """

    def __call__(self, parser, namespace, values, option_string):
        dest_dict = getattr(namespace, self.dest)
        while values:
            jid_s = values.pop(0)
            try:
                subscription = values.pop(0)
            except IndexError:
                subscription = "subscribed"
            if subscription not in ALLOWED_SUBSCRIPTIONS_OWNER:
                parser.error(
                    _("subscription must be one of {}").format(
                        ", ".join(ALLOWED_SUBSCRIPTIONS_OWNER)
                    )
                )
            dest_dict[jid_s] = subscription


class NodeSubscriptionsSet(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "set",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_verbose=True,
            help=_("set/modify subscriptions (for node owner)"),
        )

    def add_parser_options(self):
        # XXX: we use optional argument syntax for a required one because list of list of 2 elements
        #      (uses to construct dicts) don't work with positional arguments
        self.parser.add_argument(
            "-S",
            "--subscription",
            dest="subscriptions",
            default={},
            nargs="+",
            metavar=("JID [SUSBSCRIPTION]"),
            required=True,
            action=StoreSubscriptionAction,
            help=_("entity/subscription couple(s)"),
        )

    async def start(self):
        try:
            self.host.bridge.psNodeSubscriptionsSet(
                self.args.service,
                self.args.node,
                self.args.subscriptions,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't set node subscriptions: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(_("subscriptions have been set"), 1)
            self.host.quit()


class NodeSubscriptions(base.CommandBase):
    subcommands = (NodeSubscriptionsGet, NodeSubscriptionsSet)

    def __init__(self, host):
        super(NodeSubscriptions, self).__init__(
            host,
            "subscriptions",
            use_profile=False,
            help=_("get or modify node subscriptions"),
        )


class NodeSchemaSet(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "set",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_verbose=True,
            help=_("set/replace a schema"),
        )

    def add_parser_options(self):
        self.parser.add_argument("schema", help=_("schema to set (must be XML)"))

    async def start(self):
        try:
            await self.host.bridge.psSchemaSet(
                self.args.service,
                self.args.node,
                self.args.schema,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't set schema: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(_("schema has been set"), 1)
            self.host.quit()


class NodeSchemaEdit(base.CommandBase, common.BaseEdit):
    use_items = False

    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "edit",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_draft=True,
            use_verbose=True,
            help=_("edit a schema"),
        )
        common.BaseEdit.__init__(self, self.host, PUBSUB_SCHEMA_TMP_DIR)

    def add_parser_options(self):
        pass

    async def publish(self, schema):
        try:
            await self.host.bridge.psSchemaSet(
                self.args.service,
                self.args.node,
                schema,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't set schema: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(_("schema has been set"), 1)
            self.host.quit()

    async def psSchemaGetCb(self, schema):
        try:
            from lxml import etree
        except ImportError:
            self.disp(
                "lxml module must be installed to use edit, please install it "
                'with "pip install lxml"',
                error=True,
            )
            self.host.quit(1)
        content_file_obj, content_file_path = self.getTmpFile()
        schema = schema.strip()
        if schema:
            parser = etree.XMLParser(remove_blank_text=True)
            schema_elt = etree.fromstring(schema, parser)
            content_file_obj.write(
                etree.tostring(schema_elt, encoding="utf-8", pretty_print=True)
            )
            content_file_obj.seek(0)
        await self.runEditor(
            "pubsub_schema_editor_args", content_file_path, content_file_obj
        )

    async def start(self):
        try:
            schema = await self.host.bridge.psSchemaGet(
                self.args.service,
                self.args.node,
                self.profile,
            )
        except BridgeException as e:
            if e.condition == "item-not-found" or e.classname == "NotFound":
                schema = ""
            else:
                self.disp(f"can't edit schema: {e}", error=True)
                self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        await self.psSchemaGetCb(schema)


class NodeSchemaGet(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_output=C.OUTPUT_XML,
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_verbose=True,
            help=_("get schema"),
        )

    def add_parser_options(self):
        pass

    async def start(self):
        try:
            schema = await self.host.bridge.psSchemaGet(
                self.args.service,
                self.args.node,
                self.profile,
            )
        except BridgeException as e:
            if e.condition == "item-not-found" or e.classname == "NotFound":
                schema = None
            else:
                self.disp(f"can't get schema: {e}", error=True)
                self.host.quit(C.EXIT_BRIDGE_ERRBACK)

        if schema:
            await self.output(schema)
            self.host.quit()
        else:
            self.disp(_("no schema found"), 1)
            self.host.quit(C.EXIT_NOT_FOUND)


class NodeSchema(base.CommandBase):
    subcommands = (NodeSchemaSet, NodeSchemaEdit, NodeSchemaGet)

    def __init__(self, host):
        super(NodeSchema, self).__init__(
            host, "schema", use_profile=False, help=_("data schema manipulation")
        )


class Node(base.CommandBase):
    subcommands = (
        NodeInfo,
        NodeCreate,
        NodePurge,
        NodeDelete,
        NodeSet,
        NodeImport,
        NodeAffiliations,
        NodeSubscriptions,
        NodeSchema,
    )

    def __init__(self, host):
        super(Node, self).__init__(
            host, "node", use_profile=False, help=_("node handling")
        )


class Set(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "set",
            use_pubsub=True,
            use_quiet=True,
            pubsub_flags={C.NODE},
            help=_("publish a new item or update an existing one"),
        )

    def add_parser_options(self):
        NodeCreate.add_node_config_options(self.parser)
        self.parser.add_argument(
            "item",
            nargs="?",
            default="",
            help=_("id, URL of the item to update, keyword, or nothing for new item"),
        )

    async def start(self):
        element, etree = xml_tools.etreeParse(self, sys.stdin)
        element = xml_tools.getPayload(self, element)
        payload = etree.tostring(element, encoding="unicode")
        extra = {}
        publish_options = NodeCreate.get_config_options(self.args)
        if publish_options:
            extra["publish_options"] = publish_options

        try:
            published_id = await self.host.bridge.psItemSend(
                self.args.service,
                self.args.node,
                payload,
                self.args.item,
                data_format.serialise(extra),
                self.profile,
            )
        except Exception as e:
            self.disp(_("can't send item: {e}").format(e=e), error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            if published_id:
                if self.args.quiet:
                    self.disp(published_id, end="")
                else:
                    self.disp(f"Item published at {published_id}")
            else:
                self.disp("Item published")
            self.host.quit(C.EXIT_OK)


class Get(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_output=C.OUTPUT_LIST_XML,
            use_pubsub=True,
            pubsub_flags={C.NODE, C.MULTI_ITEMS},
            help=_("get pubsub item(s)"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-S",
            "--sub-id",
            default="",
            help=_("subscription id"),
        )
        #  TODO: a key(s) argument to select keys to display
        # TODO: add MAM filters

    async def start(self):
        try:
            ps_result = data_format.deserialise(
                await self.host.bridge.psItemsGet(
                    self.args.service,
                    self.args.node,
                    self.args.max,
                    self.args.items,
                    self.args.sub_id,
                    self.getPubsubExtra(),
                    self.profile,
                )
            )
        except BridgeException as e:
            if e.condition == "item-not-found" or e.classname == "NotFound":
                self.disp(
                    f"The node {self.args.node} doesn't exist on {self.args.service}",
                    error=True,
                )
                self.host.quit(C.EXIT_NOT_FOUND)
            else:
                self.disp(f"can't get pubsub items: {e}", error=True)
                self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        except Exception as e:
            self.disp(f"Internal error: {e}", error=True)
            self.host.quit(C.EXIT_INTERNAL_ERROR)
        else:
            await self.output(ps_result["items"])
            self.host.quit(C.EXIT_OK)


class Delete(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "delete",
            use_pubsub=True,
            pubsub_flags={C.NODE, C.ITEM, C.SINGLE_ITEM},
            help=_("delete an item"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-f", "--force", action="store_true", help=_("delete without confirmation")
        )
        self.parser.add_argument(
            "-N", "--notify", action="store_true", help=_("notify deletion")
        )

    async def start(self):
        if not self.args.item:
            self.parser.error(_("You need to specify an item to delete"))
        if not self.args.force:
            message = _("Are you sure to delete item {item_id} ?").format(
                item_id=self.args.item
            )
            await self.host.confirmOrQuit(message, _("item deletion cancelled"))
        try:
            await self.host.bridge.psItemRetract(
                self.args.service,
                self.args.node,
                self.args.item,
                self.args.notify,
                self.profile,
            )
        except Exception as e:
            self.disp(_("can't delete item: {e}").format(e=e), error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(_("item {item} has been deleted").format(item=self.args.item))
            self.host.quit(C.EXIT_OK)


class Edit(base.CommandBase, common.BaseEdit):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "edit",
            use_verbose=True,
            use_pubsub=True,
            pubsub_flags={C.NODE, C.SINGLE_ITEM},
            use_draft=True,
            help=_("edit an existing or new pubsub item"),
        )
        common.BaseEdit.__init__(self, self.host, PUBSUB_TMP_DIR)

    def add_parser_options(self):
        pass

    async def publish(self, content):
        published_id = await self.host.bridge.psItemSend(
            self.pubsub_service,
            self.pubsub_node,
            content,
            self.pubsub_item or "",
            "",
            self.profile,
        )
        if published_id:
            self.disp("Item published at {pub_id}".format(pub_id=published_id))
        else:
            self.disp("Item published")

    async def getItemData(self, service, node, item):
        try:
            from lxml import etree
        except ImportError:
            self.disp(
                "lxml module must be installed to use edit, please install it "
                'with "pip install lxml"',
                error=True,
            )
            self.host.quit(1)
        items = [item] if item else []
        ps_result = data_format.deserialise(
            await self.host.bridge.psItemsGet(
                service, node, 1, items, "", {}, self.profile
            )
        )
        item_raw = ps_result["items"][0]
        parser = etree.XMLParser(remove_blank_text=True, recover=True)
        item_elt = etree.fromstring(item_raw, parser)
        item_id = item_elt.get("id")
        try:
            payload = item_elt[0]
        except IndexError:
            self.disp(_("Item has not payload"), 1)
            return "", item_id
        return etree.tostring(payload, encoding="unicode", pretty_print=True), item_id

    async def start(self):
        (
            self.pubsub_service,
            self.pubsub_node,
            self.pubsub_item,
            content_file_path,
            content_file_obj,
        ) = await self.getItemPath()
        await self.runEditor("pubsub_editor_args", content_file_path, content_file_obj)
        self.host.quit()


class Rename(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "rename",
            use_pubsub=True,
            pubsub_flags={C.NODE, C.SINGLE_ITEM},
            help=_("rename a pubsub item"),
        )

    def add_parser_options(self):
        self.parser.add_argument("new_id", help=_("new item id to use"))

    async def start(self):
        try:
            await self.host.bridge.psItemRename(
                self.args.service,
                self.args.node,
                self.args.item,
                self.args.new_id,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't rename item: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp("Item renamed")
            self.host.quit(C.EXIT_OK)


class Subscribe(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "subscribe",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_verbose=True,
            help=_("subscribe to a node"),
        )

    def add_parser_options(self):
        pass

    async def start(self):
        try:
            sub_id = await self.host.bridge.psSubscribe(
                self.args.service,
                self.args.node,
                {},
                self.profile,
            )
        except Exception as e:
            self.disp(_("can't subscribe to node: {e}").format(e=e), error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(_("subscription done"), 1)
            if sub_id:
                self.disp(_("subscription id: {sub_id}").format(sub_id=sub_id))
            self.host.quit()


class Unsubscribe(base.CommandBase):
    # FIXME: check why we get a a NodeNotFound on subscribe just after unsubscribe

    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "unsubscribe",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_verbose=True,
            help=_("unsubscribe from a node"),
        )

    def add_parser_options(self):
        pass

    async def start(self):
        try:
            await self.host.bridge.psUnsubscribe(
                self.args.service,
                self.args.node,
                self.profile,
            )
        except Exception as e:
            self.disp(_("can't unsubscribe from node: {e}").format(e=e), error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(_("subscription removed"), 1)
            self.host.quit()


class Subscriptions(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "subscriptions",
            use_output=C.OUTPUT_LIST_DICT,
            use_pubsub=True,
            help=_("retrieve all subscriptions on a service"),
        )

    def add_parser_options(self):
        pass

    async def start(self):
        try:
            subscriptions = await self.host.bridge.psSubscriptionsGet(
                self.args.service,
                self.args.node,
                self.profile,
            )
        except Exception as e:
            self.disp(_("can't retrieve subscriptions: {e}").format(e=e), error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            await self.output(subscriptions)
            self.host.quit()


class Affiliations(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "affiliations",
            use_output=C.OUTPUT_DICT,
            use_pubsub=True,
            help=_("retrieve all affiliations on a service"),
        )

    def add_parser_options(self):
        pass

    async def start(self):
        try:
            affiliations = await self.host.bridge.psAffiliationsGet(
                self.args.service,
                self.args.node,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't get node affiliations: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            await self.output(affiliations)
            self.host.quit()


class Search(base.CommandBase):
    """This command do a search without using MAM

    This commands checks every items it finds by itself,
    so it may be heavy in resources both for server and client
    """

    RE_FLAGS = re.MULTILINE | re.UNICODE
    EXEC_ACTIONS = ("exec", "external")

    def __init__(self, host):
        # FIXME: C.NO_MAX is not needed here, and this can be globally removed from consts
        #        the only interest is to change the help string, but this can be explained
        #        extensively in man pages (max is for each node found)
        base.CommandBase.__init__(
            self,
            host,
            "search",
            use_output=C.OUTPUT_XML,
            use_pubsub=True,
            pubsub_flags={C.MULTI_ITEMS, C.NO_MAX},
            use_verbose=True,
            help=_("search items corresponding to filters"),
        )

    @property
    def etree(self):
        """load lxml.etree only if needed"""
        if self._etree is None:
            from lxml import etree

            self._etree = etree
        return self._etree

    def filter_opt(self, value, type_):
        return (type_, value)

    def filter_flag(self, value, type_):
        value = C.bool(value)
        return (type_, value)

    def add_parser_options(self):
        self.parser.add_argument(
            "-D",
            "--max-depth",
            type=int,
            default=0,
            help=_(
                "maximum depth of recursion (will search linked nodes if > 0, "
                "DEFAULT: 0)"
            ),
        )
        self.parser.add_argument(
            "-M",
            "--node-max",
            type=int,
            default=30,
            help=_(
                "maximum number of items to get per node ({} to get all items, "
                "DEFAULT: 30)".format(C.NO_LIMIT)
            ),
        )
        self.parser.add_argument(
            "-N",
            "--namespace",
            action="append",
            nargs=2,
            default=[],
            metavar="NAME NAMESPACE",
            help=_("namespace to use for xpath"),
        )

        # filters
        filter_text = partial(self.filter_opt, type_="text")
        filter_re = partial(self.filter_opt, type_="regex")
        filter_xpath = partial(self.filter_opt, type_="xpath")
        filter_python = partial(self.filter_opt, type_="python")
        filters = self.parser.add_argument_group(
            _("filters"),
            _("only items corresponding to following filters will be kept"),
        )
        filters.add_argument(
            "-t",
            "--text",
            action="append",
            dest="filters",
            type=filter_text,
            metavar="TEXT",
            help=_("full text filter, item must contain this string (XML included)"),
        )
        filters.add_argument(
            "-r",
            "--regex",
            action="append",
            dest="filters",
            type=filter_re,
            metavar="EXPRESSION",
            help=_("like --text but using a regular expression"),
        )
        filters.add_argument(
            "-x",
            "--xpath",
            action="append",
            dest="filters",
            type=filter_xpath,
            metavar="XPATH",
            help=_("filter items which has elements matching this xpath"),
        )
        filters.add_argument(
            "-P",
            "--python",
            action="append",
            dest="filters",
            type=filter_python,
            metavar="PYTHON_CODE",
            help=_(
                "Python expression which much return a bool (True to keep item, "
                'False to reject it). "item" is raw text item, "item_xml" is '
                "lxml's etree.Element"
            ),
        )

        # filters flags
        flag_case = partial(self.filter_flag, type_="ignore-case")
        flag_invert = partial(self.filter_flag, type_="invert")
        flag_dotall = partial(self.filter_flag, type_="dotall")
        flag_matching = partial(self.filter_flag, type_="only-matching")
        flags = self.parser.add_argument_group(
            _("filters flags"),
            _("filters modifiers (change behaviour of following filters)"),
        )
        flags.add_argument(
            "-C",
            "--ignore-case",
            action="append",
            dest="filters",
            type=flag_case,
            const=("ignore-case", True),
            nargs="?",
            metavar="BOOLEAN",
            help=_("(don't) ignore case in following filters (DEFAULT: case sensitive)"),
        )
        flags.add_argument(
            "-I",
            "--invert",
            action="append",
            dest="filters",
            type=flag_invert,
            const=("invert", True),
            nargs="?",
            metavar="BOOLEAN",
            help=_("(don't) invert effect of following filters (DEFAULT: don't invert)"),
        )
        flags.add_argument(
            "-A",
            "--dot-all",
            action="append",
            dest="filters",
            type=flag_dotall,
            const=("dotall", True),
            nargs="?",
            metavar="BOOLEAN",
            help=_("(don't) use DOTALL option for regex (DEFAULT: don't use)"),
        )
        flags.add_argument(
            "-k",
            "--only-matching",
            action="append",
            dest="filters",
            type=flag_matching,
            const=("only-matching", True),
            nargs="?",
            metavar="BOOLEAN",
            help=_("keep only the matching part of the item"),
        )

        # action
        self.parser.add_argument(
            "action",
            default="print",
            nargs="?",
            choices=("print", "exec", "external"),
            help=_("action to do on found items (DEFAULT: print)"),
        )
        self.parser.add_argument("command", nargs=argparse.REMAINDER)

    async def getItems(self, depth, service, node, items):
        self.to_get += 1
        try:
            ps_result = data_format.deserialise(
                await self.host.bridge.psItemsGet(
                    service,
                    node,
                    self.args.node_max,
                    items,
                    "",
                    self.getPubsubExtra(),
                    self.profile,
                )
            )
        except Exception as e:
            self.disp(
                f"can't get pubsub items at {service} (node: {node}): {e}",
                error=True,
            )
            self.to_get -= 1
        else:
            await self.search(ps_result, depth)

    def _checkPubsubURL(self, match, found_nodes):
        """check that the matched URL is an xmpp: one

        @param found_nodes(list[unicode]): found_nodes
            this list will be filled while xmpp: URIs are discovered
        """
        url = match.group(0)
        if url.startswith("xmpp"):
            try:
                url_data = uri.parseXMPPUri(url)
            except ValueError:
                return
            if url_data["type"] == "pubsub":
                found_node = {"service": url_data["path"], "node": url_data["node"]}
                if "item" in url_data:
                    found_node["item"] = url_data["item"]
                found_nodes.append(found_node)

    async def getSubNodes(self, item, depth):
        """look for pubsub URIs in item, and getItems on the linked nodes"""
        found_nodes = []
        checkURI = partial(self._checkPubsubURL, found_nodes=found_nodes)
        strings.RE_URL.sub(checkURI, item)
        for data in found_nodes:
            await self.getItems(
                depth + 1,
                data["service"],
                data["node"],
                [data["item"]] if "item" in data else [],
            )

    def parseXml(self, item):
        try:
            return self.etree.fromstring(item)
        except self.etree.XMLSyntaxError:
            self.disp(
                _(
                    "item doesn't looks like XML, you have probably used --only-matching "
                    "somewhere before and we have no more XML"
                ),
                error=True,
            )
            self.host.quit(C.EXIT_BAD_ARG)

    def filter(self, item):
        """apply filters given on command line

        if only-matching is used, item may be modified
        @return (tuple[bool, unicode]): a tuple with:
            - keep: True if item passed the filters
            - item: it is returned in case of modifications
        """
        ignore_case = False
        invert = False
        dotall = False
        only_matching = False
        item_xml = None
        for type_, value in self.args.filters:
            keep = True

            ## filters

            if type_ == "text":
                if ignore_case:
                    if value.lower() not in item.lower():
                        keep = False
                else:
                    if value not in item:
                        keep = False
                if keep and only_matching:
                    # doesn't really make sens to keep a fixed string
                    # so we raise an error
                    self.host.disp(
                        _("--only-matching used with fixed --text string, are you sure?"),
                        error=True,
                    )
                    self.host.quit(C.EXIT_BAD_ARG)
            elif type_ == "regex":
                flags = self.RE_FLAGS
                if ignore_case:
                    flags |= re.IGNORECASE
                if dotall:
                    flags |= re.DOTALL
                match = re.search(value, item, flags)
                keep = match != None
                if keep and only_matching:
                    item = match.group()
                    item_xml = None
            elif type_ == "xpath":
                if item_xml is None:
                    item_xml = self.parseXml(item)
                try:
                    elts = item_xml.xpath(value, namespaces=self.args.namespace)
                except self.etree.XPathEvalError as e:
                    self.disp(_("can't use xpath: {reason}").format(reason=e), error=True)
                    self.host.quit(C.EXIT_BAD_ARG)
                keep = bool(elts)
                if keep and only_matching:
                    item_xml = elts[0]
                    try:
                        item = self.etree.tostring(item_xml, encoding="unicode")
                    except TypeError:
                        # we have a string only, not an element
                        item = str(item_xml)
                        item_xml = None
            elif type_ == "python":
                if item_xml is None:
                    item_xml = self.parseXml(item)
                cmd_ns = {"etree": self.etree, "item": item, "item_xml": item_xml}
                try:
                    keep = eval(value, cmd_ns)
                except SyntaxError as e:
                    self.disp(str(e), error=True)
                    self.host.quit(C.EXIT_BAD_ARG)

                    ## flags

            elif type_ == "ignore-case":
                ignore_case = value
            elif type_ == "invert":
                invert = value
                #  we need to continue, else loop would end here
                continue
            elif type_ == "dotall":
                dotall = value
            elif type_ == "only-matching":
                only_matching = value
            else:
                raise exceptions.InternalError(
                    _("unknown filter type {type}").format(type=type_)
                )

            if invert:
                keep = not keep
            if not keep:
                return False, item

        return True, item

    async def doItemAction(self, item, metadata):
        """called when item has been kepts and the action need to be done

        @param item(unicode): accepted item
        """
        action = self.args.action
        if action == "print" or self.host.verbosity > 0:
            try:
                await self.output(item)
            except self.etree.XMLSyntaxError:
                # item is not valid XML, but a string
                # can happen when --only-matching is used
                self.disp(item)
        if action in self.EXEC_ACTIONS:
            item_elt = self.parseXml(item)
            if action == "exec":
                use = {
                    "service": metadata["service"],
                    "node": metadata["node"],
                    "item": item_elt.get("id"),
                    "profile": self.profile,
                }
                # we need to send a copy of self.args.command
                # else it would be modified
                parser_args, use_args = arg_tools.get_use_args(
                    self.host, self.args.command, use, verbose=self.host.verbosity > 1
                )
                cmd_args = sys.argv[0:1] + parser_args + use_args
            else:
                cmd_args = self.args.command

            self.disp(
                "COMMAND: {command}".format(
                    command=" ".join([arg_tools.escape(a) for a in cmd_args])
                ),
                2,
            )
            if action == "exec":
                p = await asyncio.create_subprocess_exec(*cmd_args)
                ret = await p.wait()
            else:
                p = await asyncio.create_subprocess_exec(*cmd_args, stdin=subprocess.PIPE)
                await p.communicate(item.encode(sys.getfilesystemencoding()))
                ret = p.returncode
            if ret != 0:
                self.disp(
                    A.color(
                        C.A_FAILURE,
                        _("executed command failed with exit code {ret}").format(ret=ret),
                    )
                )

    async def search(self, ps_result, depth):
        """callback of getItems

        this method filters items, get sub nodes if needed,
        do the requested action, and exit the command when everything is done
        @param items_data(tuple): result of getItems
        @param depth(int): current depth level
            0 for first node, 1 for first children, and so on
        """
        for item in ps_result["items"]:
            if depth < self.args.max_depth:
                await self.getSubNodes(item, depth)
            keep, item = self.filter(item)
            if not keep:
                continue
            await self.doItemAction(item, ps_result)

            #  we check if we got all getItems results
        self.to_get -= 1
        if self.to_get == 0:
            # yes, we can quit
            self.host.quit()
        assert self.to_get > 0

    async def start(self):
        if self.args.command:
            if self.args.action not in self.EXEC_ACTIONS:
                self.parser.error(
                    _("Command can only be used with {actions} actions").format(
                        actions=", ".join(self.EXEC_ACTIONS)
                    )
                )
        else:
            if self.args.action in self.EXEC_ACTIONS:
                self.parser.error(_("you need to specify a command to execute"))
        if not self.args.node:
            # TODO: handle get service affiliations when node is not set
            self.parser.error(_("empty node is not handled yet"))
            # to_get is increased on each get and decreased on each answer
            # when it reach 0 again, the command is finished
        self.to_get = 0
        self._etree = None
        if self.args.filters is None:
            self.args.filters = []
        self.args.namespace = dict(
            self.args.namespace + [("pubsub", "http://jabber.org/protocol/pubsub")]
        )
        await self.getItems(0, self.args.service, self.args.node, self.args.items)


class Transform(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "transform",
            use_pubsub=True,
            pubsub_flags={C.NODE, C.MULTI_ITEMS},
            help=_("modify items of a node using an external command/script"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "--apply",
            action="store_true",
            help=_("apply transformation (DEFAULT: do a dry run)"),
        )
        self.parser.add_argument(
            "--admin",
            action="store_true",
            help=_("do a pubsub admin request, needed to change publisher"),
        )
        self.parser.add_argument(
            "-I",
            "--ignore-errors",
            action="store_true",
            help=_(
                "if command return a non zero exit code, ignore the item and continue"
            ),
        )
        self.parser.add_argument(
            "-A",
            "--all",
            action="store_true",
            help=_("get all items by looping over all pages using RSM"),
        )
        self.parser.add_argument(
            "command_path",
            help=_(
                "path to the command to use. Will be called repetitivly with an "
                "item as input. Output (full item XML) will be used as new one. "
                'Return "DELETE" string to delete the item, and "SKIP" to ignore it'
            ),
        )

    async def psItemsSendCb(self, item_ids, metadata):
        if item_ids:
            self.disp(
                _("items published with ids {item_ids}").format(
                    item_ids=", ".join(item_ids)
                )
            )
        else:
            self.disp(_("items published"))
        if self.args.all:
            return await self.handleNextPage(metadata)
        else:
            self.host.quit()

    async def handleNextPage(self, metadata):
        """Retrieve new page through RSM or quit if we're in the last page

        use to handle --all option
        @param metadata(dict): metadata as returned by psItemsGet
        """
        try:
            last = metadata["rsm"]["last"]
            index = int(metadata["rsm"]["index"])
            count = int(metadata["rsm"]["count"])
        except KeyError:
            self.disp(
                _("Can't retrieve all items, RSM metadata not available"), error=True
            )
            self.host.quit(C.EXIT_MISSING_FEATURE)
        except ValueError as e:
            self.disp(
                _("Can't retrieve all items, bad RSM metadata: {msg}").format(msg=e),
                error=True,
            )
            self.host.quit(C.EXIT_ERROR)

        if index + self.args.rsm_max >= count:
            self.disp(_("All items transformed"))
            self.host.quit(0)

        self.disp(
            _("Retrieving next page ({page_idx}/{page_total})").format(
                page_idx=int(index / self.args.rsm_max) + 1,
                page_total=int(count / self.args.rsm_max),
            )
        )

        extra = self.getPubsubExtra()
        extra["rsm_after"] = last
        try:
            ps_result = await data_format.deserialise(
                self.host.bridge.psItemsGet(
                    self.args.service,
                    self.args.node,
                    self.args.rsm_max,
                    self.args.items,
                    "",
                    extra,
                    self.profile,
                )
            )
        except Exception as e:
            self.disp(f"can't retrieve items: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            await self.psItemsGetCb(ps_result)

    async def psItemsGetCb(self, ps_result):
        encoding = "utf-8"
        new_items = []

        for item in ps_result["items"]:
            if self.check_duplicates:
                # this is used when we are not ordering by creation
                # to avoid infinite loop
                item_elt, __ = xml_tools.etreeParse(self, item)
                item_id = item_elt.get("id")
                if item_id in self.items_ids:
                    self.disp(
                        _(
                            "Duplicate found on item {item_id}, we have probably handled "
                            "all items."
                        ).format(item_id=item_id)
                    )
                    self.host.quit()
                self.items_ids.append(item_id)

                # we launch the command to filter the item
            try:
                p = await asyncio.create_subprocess_exec(
                    self.args.command_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE
                )
            except OSError as e:
                exit_code = C.EXIT_CMD_NOT_FOUND if e.errno == 2 else C.EXIT_ERROR
                self.disp(f"Can't execute the command: {e}", error=True)
                self.host.quit(exit_code)
            encoding = "utf-8"
            cmd_std_out, cmd_std_err = await p.communicate(item.encode(encoding))
            ret = p.returncode
            if ret != 0:
                self.disp(
                    f"The command returned a non zero status while parsing the "
                    f"following item:\n\n{item}",
                    error=True,
                )
                if self.args.ignore_errors:
                    continue
                else:
                    self.host.quit(C.EXIT_CMD_ERROR)
            if cmd_std_err is not None:
                cmd_std_err = cmd_std_err.decode(encoding, errors="ignore")
                self.disp(cmd_std_err, error=True)
            cmd_std_out = cmd_std_out.decode(encoding).strip()
            if cmd_std_out == "DELETE":
                item_elt, __ = xml_tools.etreeParse(self, item)
                item_id = item_elt.get("id")
                self.disp(_("Deleting item {item_id}").format(item_id=item_id))
                if self.args.apply:
                    try:
                        await self.host.bridge.psItemRetract(
                            self.args.service,
                            self.args.node,
                            item_id,
                            False,
                            self.profile,
                        )
                    except Exception as e:
                        self.disp(f"can't delete item {item_id}: {e}", error=True)
                        self.host.quit(C.EXIT_BRIDGE_ERRBACK)
                continue
            elif cmd_std_out == "SKIP":
                item_elt, __ = xml_tools.etreeParse(self, item)
                item_id = item_elt.get("id")
                self.disp(_("Skipping item {item_id}").format(item_id=item_id))
                continue
            element, etree = xml_tools.etreeParse(self, cmd_std_out)

            # at this point command has been run and we have a etree.Element object
            if element.tag not in ("item", "{http://jabber.org/protocol/pubsub}item"):
                self.disp(
                    "your script must return a whole item, this is not:\n{xml}".format(
                        xml=etree.tostring(element, encoding="unicode")
                    ),
                    error=True,
                )
                self.host.quit(C.EXIT_DATA_ERROR)

            if not self.args.apply:
                # we have a dry run, we just display filtered items
                serialised = etree.tostring(
                    element, encoding="unicode", pretty_print=True
                )
                self.disp(serialised)
            else:
                new_items.append(etree.tostring(element, encoding="unicode"))

        if not self.args.apply:
            # on dry run we have nothing to wait for, we can quit
            if self.args.all:
                return await self.handleNextPage(ps_result)
            self.host.quit()
        else:
            if self.args.admin:
                bridge_method = self.host.bridge.psAdminItemsSend
            else:
                bridge_method = self.host.bridge.psItemsSend

            try:
                ps_items_send_result = await bridge_method(
                    self.args.service,
                    self.args.node,
                    new_items,
                    "",
                    self.profile,
                )
            except Exception as e:
                self.disp(f"can't send item: {e}", error=True)
                self.host.quit(C.EXIT_BRIDGE_ERRBACK)
            else:
                await self.psItemsSendCb(ps_items_send_result, metadata=ps_result)

    async def start(self):
        if self.args.all and self.args.order_by != C.ORDER_BY_CREATION:
            self.check_duplicates = True
            self.items_ids = []
            self.disp(
                A.color(
                    A.FG_RED,
                    A.BOLD,
                    '/!\\ "--all" should be used with "--order-by creation" /!\\\n',
                    A.RESET,
                    "We'll update items, so order may change during transformation,\n"
                    "we'll try to mitigate that by stopping on first duplicate,\n"
                    "but this method is not safe, and some items may be missed.\n---\n",
                )
            )
        else:
            self.check_duplicates = False

        try:
            ps_result = data_format.deserialise(
                await self.host.bridge.psItemsGet(
                    self.args.service,
                    self.args.node,
                    self.args.max,
                    self.args.items,
                    "",
                    self.getPubsubExtra(),
                    self.profile,
                )
            )
        except Exception as e:
            self.disp(f"can't retrieve items: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            await self.psItemsGetCb(ps_result)


class Uri(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "uri",
            use_profile=False,
            use_pubsub=True,
            pubsub_flags={C.NODE, C.SINGLE_ITEM},
            help=_("build URI"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-p",
            "--profile",
            default=C.PROF_KEY_DEFAULT,
            help=_("profile (used when no server is specified)"),
        )

    def display_uri(self, jid_):
        uri_args = {}
        if not self.args.service:
            self.args.service = jid.JID(jid_).bare

        for key in ("node", "service", "item"):
            value = getattr(self.args, key)
            if key == "service":
                key = "path"
            if value:
                uri_args[key] = value
        self.disp(uri.buildXMPPUri("pubsub", **uri_args))
        self.host.quit()

    async def start(self):
        if not self.args.service:
            try:
                jid_ = await self.host.bridge.asyncGetParamA(
                    "JabberID", "Connection", profile_key=self.args.profile
                )
            except Exception as e:
                self.disp(f"can't retrieve jid: {e}", error=True)
                self.host.quit(C.EXIT_BRIDGE_ERRBACK)
            else:
                self.display_uri(jid_)
        else:
            self.display_uri(None)


class HookCreate(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "create",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            help=_("create a Pubsub hook"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-t",
            "--type",
            default="python",
            choices=("python", "python_file", "python_code"),
            help=_("hook type"),
        )
        self.parser.add_argument(
            "-P",
            "--persistent",
            action="store_true",
            help=_("make hook persistent across restarts"),
        )
        self.parser.add_argument(
            "hook_arg",
            help=_("argument of the hook (depend of the type)"),
        )

    @staticmethod
    def checkArgs(self):
        if self.args.type == "python_file":
            self.args.hook_arg = os.path.abspath(self.args.hook_arg)
            if not os.path.isfile(self.args.hook_arg):
                self.parser.error(
                    _("{path} is not a file").format(path=self.args.hook_arg)
                )

    async def start(self):
        self.checkArgs(self)
        try:
            await self.host.bridge.psHookAdd(
                self.args.service,
                self.args.node,
                self.args.type,
                self.args.hook_arg,
                self.args.persistent,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't create hook: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.host.quit()


class HookDelete(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "delete",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            help=_("delete a Pubsub hook"),
        )

    def add_parser_options(self):
        self.parser.add_argument(
            "-t",
            "--type",
            default="",
            choices=("", "python", "python_file", "python_code"),
            help=_("hook type to remove, empty to remove all (DEFAULT: remove all)"),
        )
        self.parser.add_argument(
            "-a",
            "--arg",
            dest="hook_arg",
            default="",
            help=_(
                "argument of the hook to remove, empty to remove all (DEFAULT: remove all)"
            ),
        )

    async def start(self):
        HookCreate.checkArgs(self)
        try:
            nb_deleted = await self.host.bridge.psHookRemove(
                self.args.service,
                self.args.node,
                self.args.type,
                self.args.hook_arg,
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't delete hook: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            self.disp(
                _("{nb_deleted} hook(s) have been deleted").format(nb_deleted=nb_deleted)
            )
            self.host.quit()


class HookList(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "list",
            use_output=C.OUTPUT_LIST_DICT,
            help=_("list hooks of a profile"),
        )

    def add_parser_options(self):
        pass

    async def start(self):
        try:
            data = await self.host.bridge.psHookList(
                self.profile,
            )
        except Exception as e:
            self.disp(f"can't list hooks: {e}", error=True)
            self.host.quit(C.EXIT_BRIDGE_ERRBACK)
        else:
            if not data:
                self.disp(_("No hook found."))
            await self.output(data)
            self.host.quit()


class Hook(base.CommandBase):
    subcommands = (HookCreate, HookDelete, HookList)

    def __init__(self, host):
        super(Hook, self).__init__(
            host,
            "hook",
            use_profile=False,
            use_verbose=True,
            help=_("trigger action on Pubsub notifications"),
        )


class Pubsub(base.CommandBase):
    subcommands = (
        Set,
        Get,
        Delete,
        Edit,
        Rename,
        Subscribe,
        Unsubscribe,
        Subscriptions,
        Node,
        Affiliations,
        Search,
        Transform,
        Hook,
        Uri,
    )

    def __init__(self, host):
        super(Pubsub, self).__init__(
            host, "pubsub", use_profile=False, help=_("PubSub nodes/items management")
        )
