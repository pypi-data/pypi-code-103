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


from kivy import properties
from kivy.animation import Animation
from kivy.clock import Clock
from kivy_garden import modernmenu
from functools import partial


class TouchMenu(modernmenu.ModernMenu):
    pass


class TouchMenuItemBehavior:
    """Class to use on every item where a menu may appear

    main_wid attribute must be set to the class inheriting from TouchMenuBehavior
    do_item_action is the method called on simple click
    getMenuChoices must return a list of menus for long press
        menus there are dict as expected by ModernMenu
        (translated text, index and callback)
    """
    main_wid = properties.ObjectProperty()
    click_timeout = properties.NumericProperty(0.4)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        t = partial(self.open_menu, touch)
        touch.ud['menu_timeout'] = t
        Clock.schedule_once(t, self.click_timeout)
        return super(TouchMenuItemBehavior, self).on_touch_down(touch)

    def do_item_action(self, touch):
        pass

    def on_touch_up(self, touch):
        if touch.ud.get('menu_timeout'):
            Clock.unschedule(touch.ud['menu_timeout'])
            if self.collide_point(*touch.pos) and self.main_wid.menu is None:
                self.do_item_action(touch)
        return super(TouchMenuItemBehavior, self).on_touch_up(touch)

    def open_menu(self, touch, dt):
        self.main_wid.open_menu(self, touch)
        del touch.ud['menu_timeout']

    def getMenuChoices(self):
        """return choice adapted to selected item

        @return (list[dict]): choices ad expected by ModernMenu
        """
        return []


class TouchMenuBehavior:
    """Class to handle a menu appearing on long press on items

    classes using this behaviour need to have a float_layout property
    pointing the main FloatLayout.
    """
    float_layout = properties.ObjectProperty()

    def __init__(self, *args, **kwargs):
        super(TouchMenuBehavior, self).__init__(*args, **kwargs)
        self.menu = None
        self.menu_item = None

    ## menu methods ##

    def clean_fl_children(self, layout, children):
        """insure that self.menu and self.menu_item are None when menu is dimissed"""
        if self.menu is not None and self.menu not in children:
            self.menu = self.menu_item = None

    def clear_menu(self):
        """remove menu if there is one"""
        if self.menu is not None:
            self.menu.dismiss()
            self.menu = None
            self.menu_item = None

    def open_menu(self, item, touch):
        """open menu for item

        @param item(PathWidget): item when the menu has been requested
        @param touch(kivy.input.MotionEvent): touch data
        """
        if self.menu_item == item:
            return
        self.clear_menu()
        pos = self.to_widget(*touch.pos)
        choices = item.getMenuChoices()
        if not choices:
            return
        self.menu = TouchMenu(choices=choices,
                              center=pos,
                              size_hint=(None, None))
        self.float_layout.add_widget(self.menu)
        self.menu.start_display(touch)
        self.menu_item = item

    def on_float_layout(self, wid, float_layout):
        float_layout.bind(children=self.clean_fl_children)


class FilterBehavior(object):
    """class to handle items filtering with animation"""

    def __init__(self, *args, **kwargs):
        super(FilterBehavior, self).__init__(*args, **kwargs)
        self._filter_last = {}
        self._filter_anim = Animation(width = 0,
                                      height = 0,
                                      opacity = 0,
                                      d = 0.5)

    def do_filter(self, parent, text, get_child_text, width_cb, height_cb,
                  continue_tests=None):
        """filter the children

        filtered children will have a animation to set width, height and opacity to 0
        @param parent(kivy.uix.widget.Widget): parent layout of the widgets to filter
        @param text(unicode): filter text (if this text is not present in a child,
            the child is filtered out)
        @param get_child_text(callable): must retrieve child text
            child is used as sole argument
        @param width_cb(callable, int, None): method to retrieve width when opened
            child is used as sole argument, int can be used instead of callable
        @param height_cb(callable, int, None): method to retrieve height when opened
            child is used as sole argument, int can be used instead of callable
        @param continue_tests(list[callable]): list of test to skip the item
            all callables take child as sole argument.
            if any of the callable return True, the child is skipped (i.e. not filtered)
        """
        text = text.strip().lower()
        filtering = len(text)>len(self._filter_last.get(parent, ''))
        self._filter_last[parent] = text
        for child in parent.children:
            if continue_tests is not None and any((t(child) for t in continue_tests)):
                continue
            if text in get_child_text(child).lower():
                self._filter_anim.cancel(child)
                for key, method in (('width', width_cb),
                                    ('height', height_cb),
                                    ('opacity', lambda c: 1)):
                    try:
                        setattr(child, key, method(child))
                    except TypeError:
                        # method is not a callable, must be an int
                        setattr(child, key, method)
            elif (filtering
                  and child.opacity > 0
                  and not self._filter_anim.have_properties_to_animate(child)):
                self._filter_anim.start(child)
