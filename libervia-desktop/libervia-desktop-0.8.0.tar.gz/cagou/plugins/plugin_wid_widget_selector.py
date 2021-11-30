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
log = logging.getLogger(__name__)
from sat.core.i18n import _
from cagou.core.constants import Const as C
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy import properties
from kivy.uix.behaviors import ButtonBehavior
from cagou.core import cagou_widget
from cagou import G


PLUGIN_INFO = {
    "name": _("widget selector"),
    "import_name": C.WID_SELECTOR,
    "main": "WidgetSelector",
    "description": _("show available widgets and allow to select one"),
    "icon_medium": "{media}/icons/muchoslava/png/selector_no_border_blue_44.png"
}


class WidgetSelItem(ButtonBehavior, BoxLayout):
    plugin_info = properties.DictProperty()
    item = properties.ObjectProperty()

    def on_release(self, *args):
        log.debug("widget selection: {}".format(self.plugin_info["name"]))
        factory = self.plugin_info["factory"]
        G.host.switchWidget(
            self, factory(self.plugin_info, None, profiles=iter(G.host.profiles)))


class WidgetSelector(cagou_widget.CagouWidget):
    container = properties.ObjectProperty()

    def __init__(self):
        super(WidgetSelector, self).__init__()
        self.items = []
        for plugin_info in G.host.getPluggedWidgets(except_cls=self.__class__):
            item = WidgetSelItem(plugin_info=plugin_info)
            self.items.append(item.item)
            item.item.bind(minimum_width=self.adjust_width)
            self.container.add_widget(item)
        self.container.add_widget(Widget())

    def adjust_width(self, label, texture_size):
        width = max([i.minimum_width for i in self.items])
        for i in self.items:
            i.width = width

    def key_input(self, window, key, scancode, codepoint, modifier):
        # we pass to avoid default CagouWidget which is going back to default widget
        # (which is this one)
        pass

    @classmethod
    def factory(cls, plugin_info, target, profiles):
        return cls()


PLUGIN_INFO["factory"] = WidgetSelector.factory
