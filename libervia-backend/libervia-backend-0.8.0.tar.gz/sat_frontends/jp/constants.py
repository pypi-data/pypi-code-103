#!/usr/bin/env python3


# Primitivus: a SAT frontend
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

from sat_frontends.quick_frontend import constants
from sat.tools.common.ansi import ANSI as A


class Const(constants.Const):

    APP_NAME = "Libervia CLI"
    APP_COMPONENT = "CLI"
    APP_NAME_ALT = "jp"
    APP_NAME_FILE = "libervia_cli"
    CONFIG_SECTION = APP_COMPONENT.lower()
    PLUGIN_CMD = "commands"
    PLUGIN_OUTPUT = "outputs"
    OUTPUT_TEXT = "text"  # blob of unicode text
    OUTPUT_DICT = "dict"  # simple key/value dictionary
    OUTPUT_LIST = "list"
    OUTPUT_LIST_DICT = "list_dict"  # list of dictionaries
    OUTPUT_DICT_DICT = "dict_dict"  # dict  of nested dictionaries
    OUTPUT_MESS = "mess"  # messages (chat)
    OUTPUT_COMPLEX = "complex"  # complex data (e.g. multi-level dictionary)
    OUTPUT_XML = "xml"  # XML node (as unicode string)
    OUTPUT_LIST_XML = "list_xml"  # list of XML nodes (as unicode strings)
    OUTPUT_XMLUI = "xmlui"  # XMLUI as unicode string
    OUTPUT_LIST_XMLUI = "list_xmlui"  # list of XMLUI (as unicode strings)
    OUTPUT_TYPES = (
        OUTPUT_TEXT,
        OUTPUT_DICT,
        OUTPUT_LIST,
        OUTPUT_LIST_DICT,
        OUTPUT_DICT_DICT,
        OUTPUT_MESS,
        OUTPUT_COMPLEX,
        OUTPUT_XML,
        OUTPUT_LIST_XML,
        OUTPUT_XMLUI,
        OUTPUT_LIST_XMLUI,
    )
    OUTPUT_NAME_SIMPLE = "simple"
    OUTPUT_NAME_XML = "xml"
    OUTPUT_NAME_XML_RAW = "xml-raw"
    OUTPUT_NAME_JSON = "json"
    OUTPUT_NAME_JSON_RAW = "json-raw"

    # Pubsub options flags
    SERVICE = "service"  # service required
    NODE = "node"  # node required
    ITEM = "item"  # item required
    SINGLE_ITEM = "single_item"  # only one item is allowed
    MULTI_ITEMS = "multi_items"  # multiple items are allowed
    NO_MAX = "no_max"  # don't add --max option for multi items

    # ANSI
    A_HEADER = A.BOLD + A.FG_YELLOW
    A_SUBHEADER = A.BOLD + A.FG_RED
    # A_LEVEL_COLORS may be used to cycle on colors according to depth of data
    A_LEVEL_COLORS = (A_HEADER, A.BOLD + A.FG_BLUE, A.FG_MAGENTA, A.FG_CYAN)
    A_SUCCESS = A.BOLD + A.FG_GREEN
    A_FAILURE = A.BOLD + A.FG_RED
    A_WARNING = A.BOLD + A.FG_RED
    #  A_PROMPT_* is for shell
    A_PROMPT_PATH = A.BOLD + A.FG_CYAN
    A_PROMPT_SUF = A.BOLD
    # Files
    A_DIRECTORY = A.BOLD + A.FG_CYAN
    A_FILE = A.FG_WHITE
