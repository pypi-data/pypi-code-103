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

"""common simple widgets"""

import json
from functools import partial, total_ordering
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.event import EventDispatcher
from kivy.metrics import dp
from kivy import properties
from sat.core.i18n import _
from sat.core import log as logging
from sat.tools.common import data_format
from sat_frontends.quick_frontend import quick_chat
from .constants import Const as C
from .common_widgets import CategorySeparator
from .image import Image, AsyncImage
from cagou import G

log = logging.getLogger(__name__)

UNKNOWN_SYMBOL = 'Unknown symbol name'


class IconButton(ButtonBehavior, Image):
    pass


class Avatar(Image):
    data = properties.DictProperty(allownone=True)

    def on_kv_post(self, __):
        if not self.source:
            self.source = G.host.getDefaultAvatar()

    def on_data(self, __, data):
        if data is None:
            self.source = G.host.getDefaultAvatar()
        else:
            self.source = data['path']


class NotifLabel(Label):
    pass

@total_ordering
class ContactItem(BoxLayout):
    """An item from ContactList

    The item will drawn as an icon (JID avatar) with its jid below.
    If "badge_text" is set, a label with the text will be drawn above the avatar.
    """
    base_width = dp(150)
    avatar_layout = properties.ObjectProperty()
    avatar = properties.ObjectProperty()
    badge = properties.ObjectProperty(allownone=True)
    badge_text = properties.StringProperty('')
    profile = properties.StringProperty()
    data = properties.DictProperty()
    jid = properties.StringProperty('')

    def on_kv_post(self, __):
        if ((self.profile and self.jid and self.data is not None
             and ('avatar' not in self.data or 'nicknames' not in self.data))):
            G.host.bridge.identityGet(
                self.jid, ['avatar', 'nicknames'], True, self.profile,
                callback=self._identityGetCb,
                errback=partial(
                    G.host.errback,
                    message=_("Can't retrieve identity for {jid}: {{msg}}").format(
                        jid=self.jid)
                )
            )

    def _identityGetCb(self, identity_raw):
        identity_data = data_format.deserialise(identity_raw)
        self.data.update(identity_data)

    def on_badge_text(self, wid, text):
        if text:
            if self.badge is not None:
                self.badge.text = text
            else:
                self.badge = NotifLabel(
                    pos_hint={"right": 0.8, "y": 0},
                    text=text,
                )
                self.avatar_layout.add_widget(self.badge)
        else:
            if self.badge is not None:
                self.avatar_layout.remove_widget(self.badge)
                self.badge = None

    def __lt__(self, other):
        return self.jid < other.jid


class ContactButton(ButtonBehavior, ContactItem):
    pass


class JidItem(BoxLayout):
    bg_color = properties.ListProperty([0.2, 0.2, 0.2, 1])
    color = properties.ListProperty([1, 1, 1, 1])
    jid = properties.StringProperty()
    profile = properties.StringProperty()
    nick = properties.StringProperty()
    avatar = properties.ObjectProperty()

    def on_avatar(self, wid, jid_):
        if self.jid and self.profile:
            self.getImage()

    def on_jid(self, wid, jid_):
        if self.profile and self.avatar:
            self.getImage()

    def on_profile(self, wid, profile):
        if self.jid and self.avatar:
            self.getImage()

    def getImage(self):
        host = G.host
        if host.contact_lists[self.profile].isRoom(self.jid.bare):
            self.avatar.opacity = 0
            self.avatar.source = ""
        else:
            self.avatar.source = (
                host.getAvatar(self.jid, profile=self.profile)
                or host.getDefaultAvatar(self.jid)
            )


class JidButton(ButtonBehavior, JidItem):
    pass


class JidToggle(ToggleButtonBehavior, JidItem):
    selected_color = properties.ListProperty(C.COLOR_SEC_DARK)


class Symbol(Label):
    symbol_map = None
    symbol = properties.StringProperty()

    def __init__(self, **kwargs):
        if self.symbol_map is None:
            with open(G.host.app.expand('{media}/fonts/fontello/config.json')) as f:
                fontello_conf = json.load(f)
            Symbol.symbol_map = {g['css']:g['code'] for g in fontello_conf['glyphs']}

        super(Symbol, self).__init__(**kwargs)

    def on_symbol(self, instance, symbol):
        try:
            code = self.symbol_map[symbol]
        except KeyError:
            log.warning(_("Invalid symbol {symbol}").format(symbol=symbol))
        else:
            self.text = chr(code)


class SymbolButton(ButtonBehavior, Symbol):
    pass


class SymbolLabel(BoxLayout):
    symbol = properties.StringProperty("")
    text = properties.StringProperty("")
    color = properties.ListProperty(C.COLOR_SEC)
    bold = properties.BooleanProperty(True)
    symbol_wid = properties.ObjectProperty()
    label = properties.ObjectProperty()


class SymbolButtonLabel(ButtonBehavior, SymbolLabel):
    pass


class SymbolToggleLabel(ToggleButtonBehavior, SymbolLabel):
    pass


class ActionSymbol(Symbol):
    pass


class ActionIcon(BoxLayout):
    plugin_info = properties.DictProperty()

    def on_plugin_info(self, instance, plugin_info):
        self.clear_widgets()
        try:
            symbol = plugin_info['icon_symbol']
        except KeyError:
            icon_src = plugin_info['icon_medium']
            icon_wid = Image(source=icon_src, allow_stretch=True)
            self.add_widget(icon_wid)
        else:
            icon_wid = ActionSymbol(symbol=symbol)
            self.add_widget(icon_wid)


class SizedImage(AsyncImage):
    """AsyncImage sized according to C.IMG_MAX_WIDTH and C.IMG_MAX_HEIGHT"""
    # following properties are desired height/width
    # i.e. the ones specified in height/width attributes of <img>
    # (or wanted for whatever reason)
    # set to None to ignore them
    target_height = properties.NumericProperty(allownone=True)
    target_width = properties.NumericProperty(allownone=True)

    def __init__(self, **kwargs):
        # best calculated size
        self._best_width = self._best_height = 100
        super().__init__(**kwargs)

    def on_texture(self, instance, texture):
        """Adapt the size according to max size and target_*"""
        if texture is None:
            return
        max_width, max_height = dp(C.IMG_MAX_WIDTH), dp(C.IMG_MAX_HEIGHT)
        width, height = texture.size
        if self.target_width:
            width = min(width, self.target_width)
        if width > max_width:
            width = C.IMG_MAX_WIDTH

        height = width / self.image_ratio

        if self.target_height:
            height = min(height, self.target_height)

        if height > max_height:
            height = max_height
            width = height * self.image_ratio

        self.width, self.height = self._best_width, self._best_height = width, height

    def on_parent(self, instance, parent):
        if parent is not None:
            parent.bind(width=self.on_parent_width)

    def on_parent_width(self, instance, width):
        if self._best_width > width:
            self.width = width
            self.height = width / self.image_ratio
        else:
            self.width, self.height = self._best_width, self._best_height


class JidSelectorCategoryLayout(StackLayout):
    pass


class JidSelector(ScrollView, EventDispatcher):
    layout = properties.ObjectProperty(None)
    # if item_class is changed, the properties must be the same as for ContactButton
    # and ordering must be supported
    item_class = properties.ObjectProperty(ContactButton)
    add_separators = properties.ObjectProperty(True)
    # list of item to show, can be:
    #    - a well-known string which can be:
    #       * "roster": all roster jids
    #       * "opened_chats": all opened chat widgets
    #       * "bookmarks": MUC bookmarks
    #       A layout will be created each time and stored in the attribute of the same
    #       name.
    #       If add_separators is True, a CategorySeparator will be added on top of each
    #       layout.
    #    - a kivy Widget, which will be added to the layout (notable useful with
    #      common_widgets.CategorySeparator)
    #    - a callable, which must return an iterable of kwargs for ContactButton
    to_show = properties.ListProperty(['roster'])

    # TODO: roster and bookmarks must be updated in real time, like for opened_chats


    def __init__(self, **kwargs):
        self.register_event_type('on_select')
        # list of layouts containing items
        self.items_layouts = []
        # jid to list of ContactButton instances map
        self.items_map = {}
        super().__init__(**kwargs)

    def on_kv_post(self, wid):
        self.update()

    def on_select(self, wid):
        pass

    def on_parent(self, wid, parent):
        if parent is None:
            log.debug("removing listeners")
            G.host.removeListener("contactsFilled", self.onContactsFilled)
            G.host.removeListener("notification", self.onNotification)
            G.host.removeListener("notificationsClear", self.onNotificationsClear)
            G.host.removeListener(
                "widgetNew", self.onWidgetNew, ignore_missing=True)
            G.host.removeListener(
                "widgetDeleted", self.onWidgetDeleted, ignore_missing=True)
        else:
            log.debug("adding listeners")
            G.host.addListener("contactsFilled", self.onContactsFilled)
            G.host.addListener("notification", self.onNotification)
            G.host.addListener("notificationsClear", self.onNotificationsClear)

    def onContactsFilled(self, profile):
        log.debug("onContactsFilled event received")
        self.update()

    def onNotification(self, entity, notification_data, profile):
        for item in self.items_map.get(entity.bare, []):
            notifs = list(G.host.getNotifs(entity.bare, profile=profile))
            item.badge_text = str(len(notifs))

    def onNotificationsClear(self, entity, type_, profile):
        for item in self.items_map.get(entity.bare, []):
            item.badge_text = ''

    def onWidgetNew(self, wid):
        if not isinstance(wid, quick_chat.QuickChat):
            return
        item = self.getItemFromWid(wid)
        if item is None:
            return
        idx = 0
        for child in self.opened_chats.children:
            if isinstance(child, self.item_class) and child < item:
                break
            idx+=1
        self.opened_chats.add_widget(item, index=idx)

    def onWidgetDeleted(self, wid):
        if not isinstance(wid, quick_chat.QuickChat):
            return

        for child in self.opened_chats.children:
            if not isinstance(child, self.item_class):
                continue
            if child.jid.bare == wid.target.bare:
                self.opened_chats.remove_widget(child)
                break

    def _createItem(self, **kwargs):
        item = self.item_class(**kwargs)
        jid = kwargs['jid']
        self.items_map.setdefault(jid, []).append(item)
        return item

    def update(self):
        log.debug("starting update")
        self.layout.clear_widgets()
        for item in self.to_show:
            if isinstance(item, str):
                if item == 'roster':
                    self.addRosterItems()
                elif item == 'bookmarks':
                    self.addBookmarksItems()
                elif item == 'opened_chats':
                    self.addOpenedChatsItems()
                else:
                    log.error(f'unknown "to_show" magic string {item!r}')
            elif isinstance(item, Widget):
                self.layout.add_widget(item)
            elif callable(item):
                items_kwargs = item()
                for item_kwargs in items_kwargs:
                    item = self._createItem(**items_kwargs)
                    item.bind(on_press=partial(self.dispatch, 'on_select'))
                    self.layout.add_widget(item)
            else:
                log.error(f"unmanaged to_show item type: {item!r}")

    def addCategoryLayout(self, label=None):
        category_layout = JidSelectorCategoryLayout()

        if label and self.add_separators:
            category_layout.add_widget(CategorySeparator(text=label))

        self.layout.add_widget(category_layout)
        self.items_layouts.append(category_layout)
        return category_layout

    def getItemFromWid(self, wid):
        """create JidSelector item from QuickChat widget"""
        contact_list = G.host.contact_lists[wid.profile]
        try:
            data=contact_list.getItem(wid.target)
        except KeyError:
            log.warning(f"Can't find item data for {wid.target}")
            data={}
        try:
            item = self._createItem(
                jid=wid.target,
                data=data,
                profile=wid.profile,
            )
        except Exception as e:
            log.warning(f"Can't add contact {wid.target}: {e}")
            return
        notifs = list(G.host.getNotifs(wid.target, profile=wid.profile))
        if notifs:
            item.badge_text = str(len(notifs))
        item.bind(on_press=partial(self.dispatch, 'on_select'))
        return item

    def addOpenedChatsItems(self):
        G.host.addListener("widgetNew", self.onWidgetNew)
        G.host.addListener("widgetDeleted", self.onWidgetDeleted)
        self.opened_chats = category_layout = self.addCategoryLayout(_("Opened chats"))
        widgets = sorted(G.host.widgets.getWidgets(
            quick_chat.QuickChat,
            profiles = G.host.profiles,
            with_duplicates=False))

        for wid in widgets:
            item = self.getItemFromWid(wid)
            if item is None:
                continue
            category_layout.add_widget(item)

    def addRosterItems(self):
        self.roster = category_layout = self.addCategoryLayout(_("Your contacts"))
        for profile in G.host.profiles:
            contact_list = G.host.contact_lists[profile]
            for entity_jid in sorted(contact_list.roster):
                item = self._createItem(
                    jid=entity_jid,
                    data=contact_list.getItem(entity_jid),
                    profile=profile,
                )
                item.bind(on_press=partial(self.dispatch, 'on_select'))
                category_layout.add_widget(item)

    def addBookmarksItems(self):
        self.bookmarks = category_layout = self.addCategoryLayout(_("Your chat rooms"))
        for profile in G.host.profiles:
            profile_manager = G.host.profiles[profile]
            try:
                bookmarks = profile_manager._bookmarks
            except AttributeError:
                log.warning(f"no bookmark in cache for profile {profile}")
                continue

            contact_list = G.host.contact_lists[profile]
            for entity_jid in bookmarks:
                try:
                    cache = contact_list.getItem(entity_jid)
                except KeyError:
                    cache = {}
                item = self._createItem(
                    jid=entity_jid,
                    data=cache,
                    profile=profile,
                )
                item.bind(on_press=partial(self.dispatch, 'on_select'))
                category_layout.add_widget(item)
