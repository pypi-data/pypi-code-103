#!/usr/bin/env python3


# SAT plugin for Result Set Management (XEP-0059)
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

from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)

from wokkel import disco
from wokkel import iwokkel
from wokkel import rsm

from twisted.words.protocols.jabber import xmlstream
from zope.interface import implementer


PLUGIN_INFO = {
    C.PI_NAME: "Result Set Management",
    C.PI_IMPORT_NAME: "XEP-0059",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0059"],
    C.PI_MAIN: "XEP_0059",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of Result Set Management"""),
}

RSM_PREFIX = "rsm_"


class XEP_0059(object):
    # XXX: RSM management is done directly in Wokkel.

    def __init__(self, host):
        log.info(_("Result Set Management plugin initialization"))

    def getHandler(self, client):
        return XEP_0059_handler()

    def parseExtra(self, extra):
        """Parse extra dictionnary to retrieve RSM arguments

        @param extra(dict): data for parse
        @return (rsm.RSMRequest, None): request with parsed arguments
            or None if no RSM arguments have been found
        """
        if int(extra.get(RSM_PREFIX + 'max', 0)) < 0:
            raise ValueError(_("rsm_max can't be negative"))

        rsm_args = {}
        for arg in ("max", "after", "before", "index"):
            try:
                argname = "max_" if arg == "max" else arg
                rsm_args[argname] = extra.pop(RSM_PREFIX + arg)
            except KeyError:
                continue

        if rsm_args:
            return rsm.RSMRequest(**rsm_args)
        else:
            return None

    def response2dict(self, rsm_response, data=None):
        """Return a dict with RSM response

        Key set in data can be:
            - rsm_first: first item id in the page
            - rsm_last: last item id in the page
            - rsm_index: position of the first item in the full set (may be approximate)
            - rsm_count: total number of items in the full set (may be approximage)
        If a value doesn't exists, it's not set.
        All values are set as strings.
        @param rsm_response(rsm.RSMResponse): response to parse
        @param data(dict, None): dict to update with rsm_* data.
            If None, a new dict is created
        @return (dict): data dict
        """
        if data is None:
            data = {}
        if rsm_response.first is not None:
            data["first"] = rsm_response.first
        if rsm_response.last is not None:
            data["last"] = rsm_response.last
        if rsm_response.index is not None:
            data["index"] = rsm_response.index
        return data


@implementer(iwokkel.IDisco)
class XEP_0059_handler(xmlstream.XMPPHandler):

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(rsm.NS_RSM)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
