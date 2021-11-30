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


from sat.core.i18n import _
from sat.core import log as logging
from cagou.core.constants import Const as C
from cagou.core.common import JidToggle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from .behaviors import FilterBehavior
from kivy import properties
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.metrics import dp
from cagou import G
from functools import partial
import webbrowser

log = logging.getLogger(__name__)

ABOUT_TITLE = _("About {}").format(C.APP_NAME)
ABOUT_CONTENT = _("""[b]{app_name} ({app_name_alt})[/b]

[u]{app_name} version[/u]:
{version}

[u]backend version[/u]:
{backend_version}

{app_name} is a libre communication tool based on libre standard XMPP.

{app_name} is part of the "Libervia" project ({app_component} frontend)
more informations at [color=5500ff][ref=website]salut-a-toi.org[/ref][/color]
""")


class AboutContent(Label):

    def on_ref_press(self, value):
        if value == "website":
            webbrowser.open("https://salut-a-toi.org")


class AboutPopup(Popup):

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.dismiss()
        return super(AboutPopup, self).on_touch_down(touch)


class TransferItem(BoxLayout):
    plug_info = properties.DictProperty()

    def on_touch_up(self, touch):
        if not self.collide_point(*touch.pos):
            return super(TransferItem, self).on_touch_up(touch)
        else:
            transfer_menu = self.parent
            while not isinstance(transfer_menu, TransferMenu):
                transfer_menu = transfer_menu.parent
            transfer_menu.do_callback(self.plug_info)
            return True


class SideMenu(BoxLayout):
    size_hint_close = (0, 1)
    size_hint_open = (0.4, 1)
    size_close = (100, 100)
    size_open = (0, 0)
    bg_color = properties.ListProperty([0, 0, 0, 1])
    # callback will be called with arguments relevant to menu
    callback = properties.ObjectProperty()
    # call do_callback even when menu is cancelled
    callback_on_close = properties.BooleanProperty(False)
    # cancel callback need to remove the widget for UI
    # will be called with the widget to remove as argument
    cancel_cb = properties.ObjectProperty()

    def __init__(self, **kwargs):
        super(SideMenu, self).__init__(**kwargs)
        if self.cancel_cb is None:
            self.cancel_cb = self.onMenuCancelled

    def _set_anim_kw(self, kw, size_hint, size):
        """Set animation keywords

        for each value of size_hint it is used if not None,
        else size is used.
        If one value of size is bigger than the respective one of Window
        the one of Window is used
        """
        size_hint_x, size_hint_y = size_hint
        width, height = size
        if size_hint_x is not None:
            kw['size_hint_x'] = size_hint_x
        elif width is not None:
            kw['width'] = min(width, Window.width)

        if size_hint_y is not None:
            kw['size_hint_y'] = size_hint_y
        elif height is not None:
            kw['height'] = min(height, Window.height)

    def show(self, caller_wid=None):
        Window.bind(on_keyboard=self.key_input)
        G.host.app.root.add_widget(self)
        kw = {'d': 0.3, 't': 'out_back'}
        self._set_anim_kw(kw, self.size_hint_open, self.size_open)
        Animation(**kw).start(self)

    def _removeFromParent(self, anim, menu):
        # self.parent can already be None if the widget has been removed by a callback
        # before the animation started.
        if self.parent is not None:
            self.parent.remove_widget(self)

    def hide(self):
        Window.unbind(on_keyboard=self.key_input)
        kw = {'d': 0.2}
        self._set_anim_kw(kw, self.size_hint_close, self.size_close)
        anim = Animation(**kw)
        anim.bind(on_complete=self._removeFromParent)
        anim.start(self)
        if self.callback_on_close:
            self.do_callback()

    def on_touch_down(self, touch):
        # we remove the menu if we click outside
        # else we want to handle the event, but not
        # transmit it to parents
        if not self.collide_point(*touch.pos):
            self.hide()
        else:
            return super(SideMenu, self).on_touch_down(touch)
        return True

    def key_input(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            self.hide()
            return True

    def onMenuCancelled(self, wid, cleaning_cb=None):
        self._closeUI(wid)
        if cleaning_cb is not None:
            cleaning_cb()

    def _closeUI(self, wid):
        G.host.closeUI()

    def do_callback(self, *args, **kwargs):
        log.warning("callback not implemented")


class ExtraMenuItem(Button):
    pass


class ExtraSideMenu(SideMenu):
    """Menu with general app actions like showing the about widget"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        G.local_platform.on_extra_menu_init(self)

    def addItem(self, label, callback):
        self.add_widget(
            ExtraMenuItem(
                text=label,
                on_press=partial(self.onItemPress, callback=callback),
            ),
            # we want the new item above "About" and last empty Widget
            index=2)

    def onItemPress(self, *args, callback):
        self.hide()
        callback()

    def onAbout(self):
        self.hide()
        about = AboutPopup()
        about.title = ABOUT_TITLE
        about.content = AboutContent(
            text=ABOUT_CONTENT.format(
                app_name = C.APP_NAME,
                app_name_alt = C.APP_NAME_ALT,
                app_component = C.APP_COMPONENT,
                backend_version = G.host.backend_version,
                version=G.host.version
            ),
            markup=True)
        about.open()


class TransferMenu(SideMenu):
    """transfer menu which handle display and callbacks"""
    # callback will be called with path to file to transfer
    # profiles if set will be sent to transfer widget, may be used to get specific files
    profiles = properties.ObjectProperty()
    transfer_txt = properties.StringProperty()
    transfer_info = properties.ObjectProperty()
    upload_btn = properties.ObjectProperty()
    encrypted = properties.BooleanProperty(False)
    items_layout = properties.ObjectProperty()
    size_hint_close = (1, 0)
    size_hint_open = (1, 0.5)

    def __init__(self, **kwargs):
        super(TransferMenu, self).__init__(**kwargs)
        if self.profiles is None:
            self.profiles = iter(G.host.profiles)
        for plug_info in G.host.getPluggedWidgets(type_=C.PLUG_TYPE_TRANSFER):
            item = TransferItem(
                plug_info = plug_info
                )
            self.items_layout.add_widget(item)

    def on_kv_post(self, __):
        self.updateTransferInfo()

    def getTransferInfo(self):
        if self.upload_btn.state == "down":
            # upload
            if self.encrypted:
                return _(
                    "The file will be [color=00aa00][b]encrypted[/b][/color] and sent to "
                    "your server\nServer admin(s) can delete the file, but they won't be "
                    "able to see its content"
                )
            else:
                return _(
                    "Beware! The file will be sent to your server and stay "
                    "[color=ff0000][b]unencrypted[/b][/color] there\nServer admin(s) "
                    "can see the file, and they choose how, when and if it will be "
                    "deleted"
                )
        else:
            # P2P
            if self.encrypted:
                return _(
                    "The file will be sent [color=ff0000][b]unencrypted[/b][/color] "
                    "directly to your contact (it may be transiting by the "
                    "server if direct connection is not possible).\n[color=ff0000]"
                    "Please note that end-to-end encryption is not yet implemented for "
                    "P2P transfer."
                )
            else:
                return _(
                    "The file will be sent [color=ff0000][b]unencrypted[/b][/color] "
                    "directly to your contact (it [i]may be[/i] transiting by the "
                    "server if direct connection is not possible)."
                )

    def updateTransferInfo(self):
        self.transfer_info.text = self.getTransferInfo()

    def _onTransferCb(self, file_path, cleaning_cb=None, external=False, wid_cont=None):
        if not external:
            wid = wid_cont[0]
            self._closeUI(wid)
        self.callback(
            file_path,
            transfer_type = (C.TRANSFER_UPLOAD
                if self.ids['upload_btn'].state == "down" else C.TRANSFER_SEND),
            cleaning_cb=cleaning_cb,
        )

    def _check_plugin_permissions_cb(self, plug_info):
        external = plug_info.get('external', False)
        wid_cont = []
        wid_cont.append(plug_info['factory'](
            plug_info,
            partial(self._onTransferCb, external=external, wid_cont=wid_cont),
            self.cancel_cb,
            self.profiles))
        if not external:
            G.host.showExtraUI(wid_cont[0])

    def do_callback(self, plug_info):
        self.parent.remove_widget(self)
        if self.callback is None:
            log.warning("TransferMenu callback is not set")
        else:
            G.local_platform.check_plugin_permissions(
                plug_info,
                callback=partial(self._check_plugin_permissions_cb, plug_info),
                errback=lambda: G.host.addNote(
                    _("permission refused"),
                    _("this transfer menu can't be used if you refuse the requested "
                      "permission"),
                    C.XMLUI_DATA_LVL_WARNING)
            )


class EntitiesSelectorMenu(SideMenu, FilterBehavior):
    """allow to select entities from roster"""
    profiles = properties.ObjectProperty()
    layout = properties.ObjectProperty()
    instructions = properties.StringProperty(_("Please select entities"))
    filter_input = properties.ObjectProperty()
    size_hint_close = (None, 1)
    size_hint_open = (None, 1)
    size_open = (dp(250), 100)
    size_close = (0, 100)

    def __init__(self, **kwargs):
        super(EntitiesSelectorMenu, self).__init__(**kwargs)
        self.filter_input.bind(text=self.do_filter_input)
        if self.profiles is None:
            self.profiles = iter(G.host.profiles)
        for profile in self.profiles:
            for jid_, jid_data in G.host.contact_lists[profile].all_iter:
                jid_wid = JidToggle(
                    jid=jid_,
                    profile=profile)
                self.layout.add_widget(jid_wid)

    def do_callback(self):
        if self.callback is not None:
            jids = [c.jid for c in self.layout.children if c.state == 'down']
            self.callback(jids)

    def do_filter_input(self, filter_input, text):
        self.layout.spacing = 0 if text else dp(5)
        self.do_filter(self.layout,
                       text,
                       lambda c: c.jid,
                       width_cb=lambda c: c.width,
                       height_cb=lambda c: dp(70))
