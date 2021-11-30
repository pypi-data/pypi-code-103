#!/usr/bin/env python3


# SAT: a jabber client
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

""" template XMLUI parsing

XMLUI classes from this modules can then be iterated to create the template
"""

from functools import partial
from sat.core.log import getLogger
from sat_frontends.tools import xmlui
from sat_frontends.tools import jid
try:
    from jinja2 import Markup as safe
except ImportError:
    # Safe marks XHTML values as usable as it.
    # If jinja2 is not there, we can use a simple lamba
    safe = lambda x: x


log = getLogger(__name__)


## Widgets ##


class Widget(object):
    category = "widget"
    type = None
    enabled = True
    read_only = True

    def __init__(self, xmlui_parent):
        self.xmlui_parent = xmlui_parent

    @property
    def name(self):
        return self._xmlui_name


class ValueWidget(Widget):
    def __init__(self, xmlui_parent, value):
        super(ValueWidget, self).__init__(xmlui_parent)
        self.value = value

    @property
    def values(self):
        return [self.value]

    @property
    def labels(self):
        #  helper property, there is not label for ValueWidget
        # but using labels make rendering more easy (one single method to call)
        #  values are actually returned
        return [self.value]


class InputWidget(ValueWidget):
    def __init__(self, xmlui_parent, value, read_only=False):
        super(InputWidget, self).__init__(xmlui_parent, value)
        self.read_only = read_only


class OptionsWidget(Widget):
    def __init__(self, xmlui_parent, options, selected, style):
        super(OptionsWidget, self).__init__(xmlui_parent)
        self.options = options
        self.selected = selected
        self.style = style

    @property
    def values(self):
        for value, label in self.items:
            yield value

    @property
    def value(self):
        if self.multi or self.no_select or len(self.selected) != 1:
            raise ValueError(
                "Can't get value for list with multiple selections or nothing selected"
            )
        return self.selected[0]

    @property
    def labels(self):
        """return only labels from self.items"""
        for value, label in self.items:
            yield label

    @property
    def items(self):
        """return suitable items, according to style"""
        no_select = self.no_select
        for value, label in self.options:
            if no_select or value in self.selected:
                yield value, label

    @property
    def inline(self):
        return "inline" in self.style

    @property
    def no_select(self):
        return "noselect" in self.style

    @property
    def multi(self):
        return "multi" in self.style


class EmptyWidget(xmlui.EmptyWidget, Widget):
    def __init__(self, _xmlui_parent):
        Widget.__init__(self)


class TextWidget(xmlui.TextWidget, ValueWidget):
    type = "text"


class JidWidget(xmlui.JidWidget, ValueWidget):
    type = "jid"

    def __init__(self, xmlui_parent, value):
        self.value = jid.JID(value)


class LabelWidget(xmlui.LabelWidget, ValueWidget):
    type = "label"

    @property
    def for_name(self):
        try:
            return self._xmlui_for_name
        except AttributeError:
            return None


class StringWidget(xmlui.StringWidget, InputWidget):
    type = "string"


class JidInputWidget(xmlui.JidInputWidget, StringWidget):
    type = "jid"

class TextBoxWidget(xmlui.TextWidget, InputWidget):
    type = "textbox"


class XHTMLBoxWidget(xmlui.XHTMLBoxWidget, InputWidget):
    type = "xhtmlbox"

    def __init__(self, xmlui_parent, value, read_only=False):
        # XXX: XHTMLBoxWidget value must be cleaned (harmful XHTML must be removed)
        #      This is normally done in the backend, the frontends should not need to
        #      worry about it.
        super(XHTMLBoxWidget, self).__init__(
            xmlui_parent=xmlui_parent, value=safe(value), read_only=read_only)


class ListWidget(xmlui.ListWidget, OptionsWidget):
    type = "list"


## Containers ##


class Container(object):
    category = "container"
    type = None

    def __init__(self, xmlui_parent):
        self.xmlui_parent = xmlui_parent
        self.children = []

    def __iter__(self):
        return iter(self.children)

    def _xmluiAppend(self, widget):
        self.children.append(widget)

    def _xmluiRemove(self, widget):
        self.children.remove(widget)


class VerticalContainer(xmlui.VerticalContainer, Container):
    type = "vertical"


class PairsContainer(xmlui.PairsContainer, Container):
    type = "pairs"


class LabelContainer(xmlui.PairsContainer, Container):
    type = "label"


## Factory ##


class WidgetFactory(object):

    def __getattr__(self, attr):
        if attr.startswith("create"):
            cls = globals()[attr[6:]]
            return cls


## Core ##


class XMLUIPanel(xmlui.XMLUIPanel):
    widget_factory = WidgetFactory()

    def show(self, *args, **kwargs):
        raise NotImplementedError


class XMLUIDialog(xmlui.XMLUIDialog):
    dialog_factory = WidgetFactory()

    def __init__(*args, **kwargs):
        raise NotImplementedError


create = partial(xmlui.create, class_map={
    xmlui.CLASS_PANEL: XMLUIPanel,
    xmlui.CLASS_DIALOG: XMLUIDialog})
