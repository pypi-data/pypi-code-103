#!/usr/bin/env python3


# Cagou: a SàT frontend
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

from sat.core.i18n import _
from .constants import Const as C
from sat.core.log import getLogger
from sat_frontends.tools import xmlui
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.uix.switch import Switch
from kivy import properties
from cagou import G
from cagou.core import dialog
from functools import partial

log = getLogger(__name__)

## Widgets ##


class TextInputOnChange(object):

    def __init__(self):
        self._xmlui_onchange_cb = None
        self._got_focus = False

    def _xmluiOnChange(self, callback):
        self._xmlui_onchange_cb = callback

    def on_focus(self, instance, focus):
        # we need to wait for first focus, else initial value
        # will trigger a on_text
        if not self._got_focus and focus:
            self._got_focus = True

    def on_text(self, instance, new_text):
        if self._xmlui_onchange_cb is not None and self._got_focus:
            self._xmlui_onchange_cb(self)


class EmptyWidget(xmlui.EmptyWidget, Widget):

    def __init__(self, _xmlui_parent):
        Widget.__init__(self)


class TextWidget(xmlui.TextWidget, Label):

    def __init__(self, xmlui_parent, value):
        Label.__init__(self, text=value)


class LabelWidget(xmlui.LabelWidget, TextWidget):
    pass


class JidWidget(xmlui.JidWidget, TextWidget):
    pass


class StringWidget(xmlui.StringWidget, TextInput, TextInputOnChange):

    def __init__(self, xmlui_parent, value, read_only=False):
        TextInput.__init__(self, text=value)
        TextInputOnChange.__init__(self)
        self.readonly = read_only

    def _xmluiSetValue(self, value):
        self.text = value

    def _xmluiGetValue(self):
        return self.text


class TextBoxWidget(xmlui.TextBoxWidget, StringWidget):
    pass


class JidInputWidget(xmlui.JidInputWidget, StringWidget):
    pass


class ButtonWidget(xmlui.ButtonWidget, Button):

    def __init__(self, _xmlui_parent, value, click_callback):
        Button.__init__(self)
        self.text = value
        self.callback = click_callback

    def _xmluiOnClick(self, callback):
        self.callback = callback

    def on_release(self):
        self.callback(self)


class DividerWidget(xmlui.DividerWidget, Widget):
    # FIXME: not working properly + only 'line' is handled
    style = properties.OptionProperty('line',
        options=['line', 'dot', 'dash', 'plain', 'blank'])

    def __init__(self, _xmlui_parent, style="line"):
        Widget.__init__(self, style=style)


class ListWidgetItem(ToggleButton):
    value = properties.StringProperty()

    def on_release(self):
        parent = self.parent
        while parent is not None and not isinstance(parent, ListWidget):
            parent = parent.parent

        if parent is not None:
            parent.select(self)
        return super(ListWidgetItem, self).on_release()

    @property
    def selected(self):
        return self.state == 'down'

    @selected.setter
    def selected(self, value):
        self.state = 'down' if value else 'normal'


class ListWidget(xmlui.ListWidget, ScrollView):
    layout = properties.ObjectProperty()

    def __init__(self, _xmlui_parent, options, selected, flags):
        ScrollView.__init__(self)
        self.multi = 'single' not in flags
        self._values = []
        for option in options:
            self.addValue(option)
        self._xmluiSelectValues(selected)
        self._on_change = None

    @property
    def items(self):
        return self.layout.children

    def select(self, item):
        if not self.multi:
            self._xmluiSelectValues([item.value])
        if self._on_change is not None:
            self._on_change(self)

    def addValue(self, option, selected=False):
        """add a value in the list

        @param option(tuple): value, label in a tuple
        """
        self._values.append(option)
        item = ListWidgetItem()
        item.value, item.text = option
        item.selected = selected
        self.layout.add_widget(item)

    def _xmluiSelectValue(self, value):
        self._xmluiSelectValues([value])

    def _xmluiSelectValues(self, values):
        for item in self.items:
            item.selected = item.value in values
            if item.selected and not self.multi:
                self.text = item.text

    def _xmluiGetSelectedValues(self):
        return [item.value for item in self.items if item.selected]

    def _xmluiAddValues(self, values, select=True):
        values = set(values).difference([c.value for c in self.items])
        for v in values:
            self.addValue(v, select)

    def _xmluiOnChange(self, callback):
        self._on_change = callback


class JidsListWidget(ListWidget):
    # TODO: real list dedicated to jids

    def __init__(self, _xmlui_parent, jids, flags):
        ListWidget.__init__(self, _xmlui_parent, [(j,j) for j in jids], [], flags)


class PasswordWidget(xmlui.PasswordWidget, TextInput, TextInputOnChange):

    def __init__(self, _xmlui_parent, value, read_only=False):
        TextInput.__init__(self, password=True, multiline=False,
            text=value, readonly=read_only, size=(100,25), size_hint=(1,None))
        TextInputOnChange.__init__(self)

    def _xmluiSetValue(self, value):
        self.text = value

    def _xmluiGetValue(self):
        return self.text


class BoolWidget(xmlui.BoolWidget, Switch):

    def __init__(self, _xmlui_parent, state, read_only=False):
        Switch.__init__(self, active=state)
        if read_only:
            self.disabled = True

    def _xmluiSetValue(self, value):
        self.active = value

    def _xmluiGetValue(self):
        return C.BOOL_TRUE if self.active else C.BOOL_FALSE

    def _xmluiOnChange(self, callback):
        self.bind(active=lambda instance, value: callback(instance))


class IntWidget(xmlui.IntWidget, TextInput, TextInputOnChange):

    def __init__(self, _xmlui_parent, value, read_only=False):
        TextInput.__init__(self, text=value, input_filter='int', multiline=False)
        TextInputOnChange.__init__(self)
        if read_only:
            self.disabled = True

    def _xmluiSetValue(self, value):
        self.text = value

    def _xmluiGetValue(self):
        return self.text


## Containers ##


class VerticalContainer(xmlui.VerticalContainer, BoxLayout):

    def __init__(self, xmlui_parent):
        self.xmlui_parent = xmlui_parent
        BoxLayout.__init__(self)

    def _xmluiAppend(self, widget):
        self.add_widget(widget)


class PairsContainer(xmlui.PairsContainer, GridLayout):

    def __init__(self, xmlui_parent):
        self.xmlui_parent = xmlui_parent
        GridLayout.__init__(self)

    def _xmluiAppend(self, widget):
        self.add_widget(widget)


class LabelContainer(PairsContainer, xmlui.LabelContainer):
    pass


class TabsPanelContainer(TabbedPanelItem):
    layout = properties.ObjectProperty(None)

    def _xmluiAppend(self, widget):
        self.layout.add_widget(widget)


class TabsContainer(xmlui.TabsContainer, TabbedPanel):

    def __init__(self, xmlui_parent):
        self.xmlui_parent = xmlui_parent
        TabbedPanel.__init__(self, do_default_tab=False)

    def _xmluiAddTab(self, label, selected):
        tab = TabsPanelContainer(text=label)
        self.add_widget(tab)
        return tab


class AdvancedListRow(BoxLayout):
    global_index = 0
    index = properties.ObjectProperty()
    selected = properties.BooleanProperty(False)

    def __init__(self, **kwargs):
        self.global_index = AdvancedListRow.global_index
        AdvancedListRow.global_index += 1
        super(AdvancedListRow, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            parent = self.parent
            while parent is not None and not isinstance(parent, AdvancedListContainer):
                parent = parent.parent
            if parent is None:
                log.error("Can't find parent AdvancedListContainer")
            else:
                if parent.selectable:
                    self.selected = parent._xmluiToggleSelected(self)

        return super(AdvancedListRow, self).on_touch_down(touch)


class AdvancedListContainer(xmlui.AdvancedListContainer, BoxLayout):

    def __init__(self, xmlui_parent, columns, selectable='no'):
        self.xmlui_parent = xmlui_parent
        BoxLayout.__init__(self)
        self._columns = columns
        self.selectable = selectable != 'no'
        self._current_row = None
        self._selected = []
        self._xmlui_select_cb = None

    def _xmluiToggleSelected(self, row):
        """inverse selection status of an AdvancedListRow

        @param row(AdvancedListRow): row to (un)select
        @return (bool): True if row is selected
        """
        try:
            self._selected.remove(row)
        except ValueError:
            self._selected.append(row)
            if self._xmlui_select_cb is not None:
                self._xmlui_select_cb(self)
            return True
        else:
            return False

    def _xmluiAppend(self, widget):
        if self._current_row is None:
            log.error("No row set, ignoring append")
            return
        self._current_row.add_widget(widget)

    def _xmluiAddRow(self, idx):
        self._current_row = AdvancedListRow()
        self._current_row.cols = self._columns
        self._current_row.index = idx
        self.add_widget(self._current_row)

    def _xmluiGetSelectedWidgets(self):
        return self._selected

    def _xmluiGetSelectedIndex(self):
        if not self._selected:
            return None
        return self._selected[0].index

    def _xmluiOnSelect(self, callback):
        """ Call callback with widget as only argument """
        self._xmlui_select_cb = callback


## Dialogs ##


class NoteDialog(xmlui.NoteDialog):

    def __init__(self, _xmlui_parent, title, message, level):
        xmlui.NoteDialog.__init__(self, _xmlui_parent)
        self.title, self.message, self.level = title, message, level

    def _xmluiShow(self):
        G.host.addNote(self.title, self.message, self.level)


class MessageDialog(xmlui.MessageDialog, dialog.MessageDialog):

    def __init__(self, _xmlui_parent, title, message, level):
        dialog.MessageDialog.__init__(self,
                                      title=title,
                                      message=message,
                                      level=level,
                                      close_cb = self.close_cb)
        xmlui.MessageDialog.__init__(self, _xmlui_parent)

    def close_cb(self):
        self._xmluiClose()

    def _xmluiShow(self):
        G.host.addNotifUI(self)

    def _xmluiClose(self, reason=None):
        G.host.closeUI()

    def show(self, *args, **kwargs):
        G.host.showUI(self)


class ConfirmDialog(xmlui.ConfirmDialog, dialog.ConfirmDialog):

    def __init__(self, _xmlui_parent, title, message, level, buttons_set):
        dialog.ConfirmDialog.__init__(self)
        xmlui.ConfirmDialog.__init__(self, _xmlui_parent)
        self.title=title
        self.message=message
        self.no_cb = self.no_cb
        self.yes_cb = self.yes_cb

    def no_cb(self):
        G.host.closeUI()
        self._xmluiCancelled()

    def yes_cb(self):
        G.host.closeUI()
        self._xmluiValidated()

    def _xmluiShow(self):
        G.host.addNotifUI(self)

    def _xmluiClose(self, reason=None):
        G.host.closeUI()

    def show(self, *args, **kwargs):
        assert kwargs["force"]
        G.host.showUI(self)


class FileDialog(xmlui.FileDialog, BoxLayout):
    message = properties.ObjectProperty()

    def __init__(self, _xmlui_parent, title, message, level, filetype):
        xmlui.FileDialog.__init__(self, _xmlui_parent)
        BoxLayout.__init__(self)
        self.message.text = message
        if filetype == C.XMLUI_DATA_FILETYPE_DIR:
            self.file_chooser.dirselect = True

    def _xmluiShow(self):
        G.host.addNotifUI(self)

    def _xmluiClose(self, reason=None):
        # FIXME: notif UI is not removed if dialog is not shown yet
        G.host.closeUI()

    def onSelect(self, path):
        try:
            path = path[0]
        except IndexError:
            path = None
        if not path:
            self._xmluiCancelled()
        else:
            self._xmluiValidated({'path': path})

    def show(self, *args, **kwargs):
        assert kwargs["force"]
        G.host.showUI(self)


## Factory ##


class WidgetFactory(object):

    def __getattr__(self, attr):
        if attr.startswith("create"):
            cls = globals()[attr[6:]]
            return cls


## Core ##


class Title(Label):

    def __init__(self, *args, **kwargs):
        kwargs['size'] = (100, 25)
        kwargs['size_hint'] = (1,None)
        super(Title, self).__init__(*args, **kwargs)


class FormButton(Button):
    pass

class SubmitButton(FormButton):
    pass

class CancelButton(FormButton):
    pass

class SaveButton(FormButton):
    pass


class XMLUIPanel(xmlui.XMLUIPanel, ScrollView):
    widget_factory = WidgetFactory()
    layout = properties.ObjectProperty()

    def __init__(self, host, parsed_xml, title=None, flags=None, callback=None,
                 ignore=None, whitelist=None, profile=C.PROF_KEY_NONE):
        ScrollView.__init__(self)
        self.close_cb = None
        self._post_treats = []  # list of callback to call after UI is constructed

        # used to workaround touch issues when a ScrollView is used inside this
        # one. This happens notably when a TabsContainer is used as main container
        # (this is the case with settings).
        self._skip_scroll_events = False
        xmlui.XMLUIPanel.__init__(self,
                                  host,
                                  parsed_xml,
                                  title=title,
                                  flags=flags,
                                  callback=callback,
                                  ignore=ignore,
                                  whitelist=whitelist,
                                  profile=profile)
        self.bind(height=self.onHeight)

    def on_touch_down(self, touch, after=False):
        if self._skip_scroll_events:
            return super(ScrollView, self).on_touch_down(touch)
        else:
            return super(XMLUIPanel, self).on_touch_down(touch)

    def on_touch_up(self, touch, after=False):
        if self._skip_scroll_events:
            return super(ScrollView, self).on_touch_up(touch)
        else:
            return super(XMLUIPanel, self).on_touch_up(touch)

    def on_touch_move(self, touch, after=False):
        if self._skip_scroll_events:
            return super(ScrollView, self).on_touch_move(touch)
        else:
            return super(XMLUIPanel, self).on_touch_move(touch)

    def setCloseCb(self, close_cb):
        self.close_cb = close_cb

    def _xmluiClose(self, __=None, reason=None):
        if self.close_cb is not None:
            self.close_cb(self, reason)
        else:
            G.host.closeUI()

    def onParamChange(self, ctrl):
        super(XMLUIPanel, self).onParamChange(ctrl)
        self.save_btn.disabled = False

    def addPostTreat(self, callback):
        self._post_treats.append(callback)

    def _postTreatCb(self):
        for cb in self._post_treats:
            cb()
        del self._post_treats

    def _saveButtonCb(self, button):
        button.disabled = True
        self.onSaveParams(button)

    def constructUI(self, parsed_dom):
        xmlui.XMLUIPanel.constructUI(self, parsed_dom, self._postTreatCb)
        if self.xmlui_title:
            self.layout.add_widget(Title(text=self.xmlui_title))
        if isinstance(self.main_cont, TabsContainer):
            # cf. comments above
            self._skip_scroll_events = True
        self.layout.add_widget(self.main_cont)
        if self.type == 'form':
            submit_btn = SubmitButton()
            submit_btn.bind(on_press=self.onFormSubmitted)
            self.layout.add_widget(submit_btn)
            if not 'NO_CANCEL' in self.flags:
                cancel_btn = CancelButton(text=_("Cancel"))
                cancel_btn.bind(on_press=self.onFormCancelled)
                self.layout.add_widget(cancel_btn)
        elif self.type == 'param':
            self.save_btn = SaveButton(text=_("Save"), disabled=True)
            self.save_btn.bind(on_press=self._saveButtonCb)
            self.layout.add_widget(self.save_btn)
        elif self.type == 'window':
            cancel_btn = CancelButton(text=_("Cancel"))
            cancel_btn.bind(
                on_press=partial(self._xmluiClose, reason=C.XMLUI_DATA_CANCELLED))
            self.layout.add_widget(cancel_btn)

    def onHeight(self, __, height):
        if isinstance(self.main_cont, TabsContainer):
            other_children_height = sum([c.height for c in self.layout.children
                                         if c is not self.main_cont])
            self.main_cont.height = height - other_children_height

    def show(self, *args, **kwargs):
        if not self.user_action and not kwargs.get("force", False):
            G.host.addNotifUI(self)
        else:
            G.host.showUI(self)


class XMLUIDialog(xmlui.XMLUIDialog):
    dialog_factory = WidgetFactory()


create = partial(xmlui.create, class_map={
    xmlui.CLASS_PANEL: XMLUIPanel,
    xmlui.CLASS_DIALOG: XMLUIDialog})
