#! /usr/bin/env python3


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
"""Standard outputs"""


from sat_frontends.jp.constants import Const as C
from sat_frontends.jp import xmlui_manager
from sat.core.log import getLogger

log = getLogger(__name__)


__outputs__ = ["XMLUI"]


class XMLUI(object):
    """Outputs for XMLUI"""

    def __init__(self, host):
        self.host = host
        host.register_output(C.OUTPUT_XMLUI, "simple", self.xmlui, default=True)
        host.register_output(
            C.OUTPUT_LIST_XMLUI, "simple", self.xmlui_list, default=True
        )

    async def xmlui(self, data):
        xmlui = xmlui_manager.create(self.host, data)
        await xmlui.show(values_only=True, read_only=True)
        self.host.disp("")

    async def xmlui_list(self, data):
        for d in data:
            await self.xmlui(d)
