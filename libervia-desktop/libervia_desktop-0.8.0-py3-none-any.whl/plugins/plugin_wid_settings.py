#!/usr/bin/env python3


# Cagou: desktop/mobile frontend for Salut à Toi XMPP client
# Copyright (C) 2016-2021 Jérôme Poisson (goffi@goffi.org)

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


from sat.core import log as logging
from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.tools.common import data_format
from sat_frontends.quick_frontend import quick_widgets
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from cagou.core import cagou_widget
from cagou import G


log = logging.getLogger(__name__)


PLUGIN_INFO = {
    "name": _("settings"),
    "main": "CagouSettings",
    "description": _("Cagou/SàT settings"),
    "icon_symbol": "wrench",
}


class CagouSettings(quick_widgets.QuickWidget, cagou_widget.CagouWidget):
    # XXX: this class can't be called "Settings", because Kivy has already a class
    #      of this name, and the kv there would apply

    def __init__(self, host, target, profiles):
        quick_widgets.QuickWidget.__init__(self, G.host, target, profiles)
        cagou_widget.CagouWidget.__init__(self)
        # the Widget() avoid CagouWidget header to be down at the beginning
        # then up when the UI is loaded
        self.loading_widget = Widget()
        self.add_widget(self.loading_widget)
        extra = {}
        G.local_platform.updateParamsExtra(extra)
        G.host.bridge.getParamsUI(
            -1, C.APP_NAME, data_format.serialise(extra), self.profile,
            callback=self.getParamsUICb,
            errback=self.getParamsUIEb)

    def changeWidget(self, widget):
        self.clear_widgets([self.loading_widget])
        del self.loading_widget
        self.add_widget(widget)

    def getParamsUICb(self, xmlui):
        G.host.actionManager({"xmlui": xmlui}, ui_show_cb=self.changeWidget, profile=self.profile)

    def getParamsUIEb(self, failure):
        self.changeWidget(Label(
            text=_("Can't load parameters!"),
            bold=True,
            color=(1,0,0,1)))
        G.host.showDialog("Can't load params UI", str(failure), "error")
