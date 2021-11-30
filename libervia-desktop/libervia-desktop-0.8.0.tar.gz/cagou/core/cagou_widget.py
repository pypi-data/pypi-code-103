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


from functools import total_ordering
from sat.core import log as logging
from sat.core import exceptions
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy import properties
from cagou import G
from .common import ActionIcon
from . import menu


log = logging.getLogger(__name__)


class HeaderChoice(ButtonBehavior, BoxLayout):
    pass


class HeaderChoiceWidget(HeaderChoice):
    cagou_widget = properties.ObjectProperty()
    plugin_info = properties.ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_release=lambda btn: self.cagou_widget.switchWidget(
            self.plugin_info))


class HeaderChoiceExtraMenu(HeaderChoice):
    pass


class HeaderWidgetCurrent(ButtonBehavior, ActionIcon):
    pass


class HeaderWidgetSelector(DropDown):

    def __init__(self, cagou_widget):
        super(HeaderWidgetSelector, self).__init__()
        plg_info_cls = cagou_widget.plugin_info_class or cagou_widget.__class__
        for plugin_info in G.host.getPluggedWidgets(except_cls=plg_info_cls):
            choice = HeaderChoiceWidget(
                cagou_widget=cagou_widget,
                plugin_info=plugin_info,
            )
            self.add_widget(choice)
        main_menu = HeaderChoiceExtraMenu(on_press=self.on_extra_menu)
        self.add_widget(main_menu)

    def add_widget(self, *args):
        widget = args[0]
        widget.bind(minimum_width=self.set_width)
        return super(HeaderWidgetSelector, self).add_widget(*args)

    def set_width(self, choice, minimum_width):
        self.width = max([c.minimum_width for c in self.container.children])

    def on_extra_menu(self, *args):
        self.dismiss()
        menu.ExtraSideMenu().show()


@total_ordering
class CagouWidget(BoxLayout):
    main_container = properties.ObjectProperty(None)
    header_input = properties.ObjectProperty(None)
    header_box = properties.ObjectProperty(None)
    use_header_input = False
    # set to True if you want to be able to switch between visible widgets of this
    # class using a carousel
    collection_carousel = False
    # set to True if you a global ScreenManager global to all widgets of this class.
    # The screen manager is created in WHWrapper
    global_screen_manager = False
    # override this if a specific class (i.e. not self.__class__) must be used for
    # plugin info. Useful when a CagouWidget is used with global_screen_manager.
    plugin_info_class = None

    def __init__(self, **kwargs):
        plg_info_cls = self.plugin_info_class or self.__class__
        for p in G.host.getPluggedWidgets():
            if p['main'] == plg_info_cls:
                self.plugin_info = p
                break
        super().__init__(**kwargs)
        self.selector = HeaderWidgetSelector(self)
        if self.use_header_input:
            self.header_input = TextInput(
                background_normal=G.host.app.expand(
                    '{media}/misc/borders/border_hollow_light.png'),
                multiline=False,
            )
            self.header_input.bind(
                on_text_validate=lambda *args: self.onHeaderInput(),
                text=self.onHeaderInputComplete,
            )
            self.header_box.add_widget(self.header_input)

    def __lt__(self, other):
        # XXX: sorting is notably used when collection_carousel is set
        try:
            target = str(self.target)
        except AttributeError:
            target = str(list(self.targets)[0])
            other_target = str(list(other.targets)[0])
        else:
            other_target = str(other.target)
        return target < other_target

    @property
    def screen_manager(self):
        if ((not self.global_screen_manager
             and not (self.plugin_info_class is not None
                      and self.plugin_info_class.global_screen_manager))):
            raise exceptions.InternalError(
                "screen_manager property can't be used if global_screen_manager is not "
                "set")
        screen = self.getAncestor(Screen)
        if screen is None:
            raise exceptions.NotFound("Can't find parent Screen")
        if screen.manager is None:
            raise exceptions.NotFound("Can't find parent ScreenManager")
        return screen.manager

    @property
    def whwrapper(self):
        """Retrieve parent widget handler"""
        return G.host.getParentWHWrapper(self)

    def screenManagerInit(self, screen_manager):
        """Override this method to do init when ScreenManager is instantiated

        This is only called once even if collection_carousel is used.
        """
        if not self.global_screen_manager:
            raise exceptions.InternalError("screenManagerInit should not be called")

    def getAncestor(self, cls):
        """Helper method to use host.getAncestorWidget with self"""
        return G.host.getAncestorWidget(self, cls)

    def switchWidget(self, plugin_info):
        self.selector.dismiss()
        factory = plugin_info["factory"]
        new_widget = factory(plugin_info, None, iter(G.host.profiles))
        G.host.switchWidget(self, new_widget)

    def key_input(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            # we go back to root screen
            G.host.switchWidget(self)
            return True

    def onHeaderInput(self):
        log.info("header input text entered")

    def onHeaderInputComplete(self, wid, text):
        return

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            G.host.selected_widget = self
        return super(CagouWidget, self).on_touch_down(touch)

    def headerInputAddExtra(self, widget):
        """add a widget on the right of header input"""
        self.header_box.add_widget(widget)

    def onVisible(self):
        pass
        # log.debug(u"{self} is visible".format(self=self))

    def onNotVisible(self):
        pass
        # log.debug(u"{self} is not visible anymore".format(self=self))
