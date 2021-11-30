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


from functools import partial
from pathlib import Path
import sys
import uuid
import mimetypes
from urllib.parse import urlparse
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, NoTransition
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix import screenmanager
from kivy.uix.behaviors import ButtonBehavior
from kivy.metrics import sp, dp
from kivy.clock import Clock
from kivy import properties
from kivy.uix.stacklayout import StackLayout
from kivy.uix.dropdown import DropDown
from kivy.core.window import Window
from sat.core import log as logging
from sat.core.i18n import _
from sat.core import exceptions
from sat.tools.common import data_format
from sat_frontends.quick_frontend import quick_widgets
from sat_frontends.quick_frontend import quick_chat
from sat_frontends.tools import jid
from cagou import G
from ..core.constants import Const as C
from ..core import cagou_widget
from ..core import xmlui
from ..core.image import Image, AsyncImage
from ..core.common import Symbol, SymbolButton, JidButton, ContactButton
from ..core.behaviors import FilterBehavior
from ..core import menu
from ..core.common_widgets import ImagesGallery

log = logging.getLogger(__name__)

PLUGIN_INFO = {
    "name": _("chat"),
    "main": "Chat",
    "description": _("instant messaging with one person or a group"),
    "icon_symbol": "chat",
}

# FIXME: OTR specific code is legacy, and only used nowadays for lock color
# we can probably get rid of them.
OTR_STATE_UNTRUSTED = 'untrusted'
OTR_STATE_TRUSTED = 'trusted'
OTR_STATE_TRUST = (OTR_STATE_UNTRUSTED, OTR_STATE_TRUSTED)
OTR_STATE_UNENCRYPTED = 'unencrypted'
OTR_STATE_ENCRYPTED = 'encrypted'
OTR_STATE_ENCRYPTION = (OTR_STATE_UNENCRYPTED, OTR_STATE_ENCRYPTED)

SYMBOL_UNENCRYPTED = 'lock-open'
SYMBOL_ENCRYPTED = 'lock'
SYMBOL_ENCRYPTED_TRUSTED = 'lock-filled'
COLOR_UNENCRYPTED = (0.4, 0.4, 0.4, 1)
COLOR_ENCRYPTED = (0.4, 0.4, 0.4, 1)
COLOR_ENCRYPTED_TRUSTED = (0.29,0.87,0.0,1)

# below this limit, new messages will be prepended
INFINITE_SCROLL_LIMIT = dp(600)

# File sending progress
PROGRESS_UPDATE = 0.2 # number of seconds before next progress update


# FIXME: a ScrollLayout was supposed to be used here, but due
#   to https://github.com/kivy/kivy/issues/6745, a StackLayout is used for now
class AttachmentsLayout(StackLayout):
    """Layout for attachments in a received message"""
    padding = properties.VariableListProperty([dp(5), dp(5), 0, dp(5)])
    attachments = properties.ObjectProperty()


class AttachmentsToSend(BoxLayout):
    """Layout for attachments to be sent with current message"""
    attachments = properties.ObjectProperty()
    reduce_checkbox = properties.ObjectProperty()
    show_resize = properties.BooleanProperty(False)

    def on_kv_post(self, __):
        self.attachments.bind(children=self.onAttachment)

    def onAttachment(self, __, attachments):
        if len(attachments) == 0:
            self.show_resize = False


class BaseAttachmentItem(BoxLayout):
    data = properties.DictProperty()
    progress = properties.NumericProperty(0)


class AttachmentItem(BaseAttachmentItem):

    def get_symbol(self, data):
        media_type = data.get(C.MESS_KEY_ATTACHMENTS_MEDIA_TYPE, '')
        main_type = media_type.split('/', 1)[0]
        if main_type == 'image':
            return "file-image"
        elif main_type == 'video':
            return "file-video"
        elif main_type == 'audio':
            return "file-audio"
        else:
            return "doc"

    def on_press(self):
        url = self.data.get('url')
        if url:
            G.local_platform.open_url(url, self)
        else:
            log.warning(f"can't find URL in {self.data}")


class AttachmentImageItem(ButtonBehavior, BaseAttachmentItem):
    image = properties.ObjectProperty()

    def on_press(self):
        full_size_source = self.data.get('path', self.data.get('url'))
        gallery = ImagesGallery(sources=[full_size_source])
        G.host.showExtraUI(gallery)

    def on_kv_post(self, __):
        self.on_data(None, self.data)

    def on_data(self, __, data):
        if self.image is None:
            return
        source = data.get('preview') or data.get('path') or data.get('url')
        if source:
            self.image.source = source


class AttachmentImagesCollectionItem(ButtonBehavior, GridLayout):
    attachments = properties.ListProperty([])
    chat = properties.ObjectProperty()
    mess_data = properties.ObjectProperty()

    def _setPreview(self, attachment, wid, preview_path):
        attachment['preview'] = preview_path
        wid.source = preview_path

    def _setPath(self, attachment, wid, path):
        attachment['path'] = path
        if wid is not None:
            # we also need a preview for the widget
            if 'preview' in attachment:
                wid.source = attachment['preview']
            else:
                G.host.bridge.imageGeneratePreview(
                    path,
                    self.chat.profile,
                    callback=partial(self._setPreview, attachment, wid),
                )

    def on_kv_post(self, __):
        attachments = self.attachments
        self.clear_widgets()
        for idx, attachment in enumerate(attachments):
            try:
                url = attachment['url']
            except KeyError:
                url = None
                to_download = False
            else:
                if url.startswith("aesgcm:"):
                    del attachment['url']
                    # if the file is encrypted, we need to download it for decryption
                    to_download = True
                else:
                    to_download = False

            if idx < 3 or len(attachments) <= 4:
                if ((self.mess_data.own_mess
                     or self.chat.contact_list.isInRoster(self.mess_data.from_jid))):
                    wid = AsyncImage(size_hint=(1, 1), source="data/images/image-loading.gif")
                    if 'preview' in attachment:
                        wid.source = attachment["preview"]
                    elif 'path' in attachment:
                        G.host.bridge.imageGeneratePreview(
                            attachment['path'],
                            self.chat.profile,
                            callback=partial(self._setPreview, attachment, wid),
                        )
                    elif url is None:
                        log.warning(f"Can't find any source for {attachment}")
                    else:
                        # we'll download the file, the preview will then be generated
                        to_download = True
                else:
                    # we don't download automatically the image if the contact is not
                    # in roster, to avoid leaking the ip
                    wid = Symbol(symbol="file-image")
                self.add_widget(wid)
            else:
                wid = None

            if to_download:
                # the file needs to be downloaded, the widget source,
                # attachment path, and preview will then be completed
                G.host.downloadURL(
                    url,
                    callback=partial(self._setPath, attachment, wid),
                    dest=C.FILE_DEST_CACHE,
                    profile=self.chat.profile,
                )

        if len(attachments) > 4:
            counter = Label(
                bold=True,
                text=f"+{len(attachments) - 3}",
            )
            self.add_widget(counter)

    def on_press(self):
        sources = []
        for attachment in self.attachments:
            source = attachment.get('path') or attachment.get('url')
            if not source:
                log.warning(f"no source for {attachment}")
            else:
                sources.append(source)
        gallery = ImagesGallery(sources=sources)
        G.host.showExtraUI(gallery)


class AttachmentToSendItem(AttachmentItem):
    # True when the item is being sent
    sending = properties.BooleanProperty(False)


class MessAvatar(ButtonBehavior, Image):
    pass


class MessageWidget(quick_chat.MessageWidget, BoxLayout):
    mess_data = properties.ObjectProperty()
    mess_xhtml = properties.ObjectProperty()
    mess_padding = (dp(5), dp(5))
    avatar = properties.ObjectProperty()
    delivery = properties.ObjectProperty()
    font_size = properties.NumericProperty(sp(12))
    right_part = properties.ObjectProperty()
    header_box = properties.ObjectProperty()

    def on_kv_post(self, __):
        if not self.mess_data:
            raise exceptions.InternalError(
                "mess_data must always be set in MessageWidget")

        self.mess_data.widgets.add(self)
        self.add_attachments()

    @property
    def chat(self):
        """return parent Chat instance"""
        return self.mess_data.parent

    def _get_from_mess_data(self, name, default):
        if self.mess_data is None:
            return default
        return getattr(self.mess_data, name)

    def _get_message(self):
        """Return currently displayed message"""
        if self.mess_data is None:
            return ""
        return self.mess_data.main_message

    def _set_message(self, message):
        if self.mess_data is None:
            return False
        if message == self.mess_data.message.get(""):
            return False
        self.mess_data.message = {"": message}
        return True

    message = properties.AliasProperty(
        partial(_get_from_mess_data, name="main_message", default=""),
        _set_message,
        bind=['mess_data'],
    )
    message_xhtml = properties.AliasProperty(
        partial(_get_from_mess_data, name="main_message_xhtml", default=""),
        bind=['mess_data'])
    mess_type = properties.AliasProperty(
        partial(_get_from_mess_data, name="type", default=""), bind=['mess_data'])
    own_mess = properties.AliasProperty(
        partial(_get_from_mess_data, name="own_mess", default=False), bind=['mess_data'])
    nick = properties.AliasProperty(
        partial(_get_from_mess_data, name="nick", default=""), bind=['mess_data'])
    time_text = properties.AliasProperty(
        partial(_get_from_mess_data, name="time_text", default=""), bind=['mess_data'])

    @property
    def info_type(self):
        return self.mess_data.info_type

    def update(self, update_dict):
        if 'avatar' in update_dict:
            avatar_data = update_dict['avatar']
            if avatar_data is None:
                source = G.host.getDefaultAvatar()
            else:
                source = avatar_data['path']
            self.avatar.source = source
        if 'status' in update_dict:
            status = update_dict['status']
            self.delivery.text =  '\u2714' if status == 'delivered' else ''

    def _setPath(self, data, path):
        """Set path of decrypted file to an item"""
        data['path'] = path

    def add_attachments(self):
        """Add attachments layout + attachments item"""
        attachments = self.mess_data.attachments
        if not attachments:
            return
        root_layout = AttachmentsLayout()
        self.right_part.add_widget(root_layout)
        layout = root_layout.attachments

        image_attachments = []
        other_attachments = []
        # we first separate images and other attachments, so we know if we need
        # to use an image collection
        for attachment in attachments:
            media_type = attachment.get(C.MESS_KEY_ATTACHMENTS_MEDIA_TYPE, '')
            main_type = media_type.split('/', 1)[0]
            # GIF images are really badly handled by Kivy, the memory
            # consumption explode, and the images frequencies are not handled
            # correctly, thus we can't display them and we consider them as
            # other attachment, so user can open the item with appropriate
            # software.
            if main_type == 'image' and media_type != "image/gif":
                image_attachments.append(attachment)
            else:
                other_attachments.append(attachment)

        if len(image_attachments) > 1:
            collection = AttachmentImagesCollectionItem(
                attachments=image_attachments,
                chat=self.chat,
                mess_data=self.mess_data,
            )
            layout.add_widget(collection)
        elif image_attachments:
            attachment = image_attachments[0]
            # to avoid leaking IP address, we only display image if the contact is in
            # roster
            if ((self.mess_data.own_mess
                 or self.chat.contact_list.isInRoster(self.mess_data.from_jid))):
                try:
                    url = urlparse(attachment['url'])
                except KeyError:
                    item = AttachmentImageItem(data=attachment)
                else:
                    if url.scheme == "aesgcm":
                        # we remove the URL now, we'll replace it by
                        # the local decrypted version
                        del attachment['url']
                        item = AttachmentImageItem(data=attachment)
                        G.host.downloadURL(
                            url.geturl(),
                            callback=partial(self._setPath, item.data),
                            dest=C.FILE_DEST_CACHE,
                            profile=self.chat.profile,
                        )
                    else:
                        item = AttachmentImageItem(data=attachment)
            else:
                item = AttachmentItem(data=attachment)

            layout.add_widget(item)

        for attachment in other_attachments:
            item = AttachmentItem(data=attachment)
            layout.add_widget(item)


class MessageInputBox(BoxLayout):
    message_input = properties.ObjectProperty()

    def send_text(self):
        self.message_input.send_text()


class MessageInputWidget(TextInput):

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        # We don't send text when shift is pressed to be able to add line feeds
        # (i.e. multi-lines messages). We don't send on Android either as the
        # send button appears on this platform.
        if (keycode[-1] == "enter"
            and "shift" not in modifiers
            and sys.platform != 'android'):
            self.send_text()
        else:
            return super(MessageInputWidget, self).keyboard_on_key_down(
                window, keycode, text, modifiers)

    def send_text(self):
        self.dispatch('on_text_validate')


class TransferButton(SymbolButton):
    chat = properties.ObjectProperty()

    def on_release(self, *args):
        menu.TransferMenu(
            encrypted=self.chat.encrypted,
            callback=self.chat.transferFile,
        ).show(self)


class ExtraMenu(DropDown):
    chat = properties.ObjectProperty()

    def on_select(self, menu):
        if menu == 'bookmark':
            G.host.bridge.menuLaunch(C.MENU_GLOBAL, ("groups", "bookmarks"),
                                     {}, C.NO_SECURITY_LIMIT, self.chat.profile,
                                     callback=partial(
                                        G.host.actionManager, profile=self.chat.profile),
                                     errback=G.host.errback)
        elif menu == 'close':
            if self.chat.type == C.CHAT_GROUP:
                # for MUC, we have to indicate the backend that we've left
                G.host.bridge.mucLeave(self.chat.target, self.chat.profile)
            else:
                # for one2one, backend doesn't keep any state, so we just delete the
                # widget here in the frontend
                G.host.widgets.deleteWidget(
                    self.chat, all_instances=True, explicit_close=True)
        else:
            raise exceptions.InternalError("Unknown menu: {}".format(menu))


class ExtraButton(SymbolButton):
    chat = properties.ObjectProperty()


class EncryptionMainButton(SymbolButton):

    def __init__(self, chat, **kwargs):
        """
        @param chat(Chat): Chat instance
        """
        self.chat = chat
        self.encryption_menu = EncryptionMenu(chat)
        super(EncryptionMainButton, self).__init__(**kwargs)
        self.bind(on_release=self.encryption_menu.open)

    def selectAlgo(self, name):
        """Mark an encryption algorithm as selected.

        This will also deselect all other button
        @param name(unicode, None): encryption plugin name
            None for plain text
        """
        buttons = self.encryption_menu.container.children
        buttons[-1].selected = name is None
        for button in buttons[:-1]:
            button.selected = button.text == name

    def getColor(self):
        if self.chat.otr_state_encryption == OTR_STATE_UNENCRYPTED:
            return  (0.4, 0.4, 0.4, 1)
        elif self.chat.otr_state_trust == OTR_STATE_TRUSTED:
            return (0.29,0.87,0.0,1)
        else:
            return  (0.4, 0.4, 0.4, 1)

    def getSymbol(self):
        if self.chat.otr_state_encryption == OTR_STATE_UNENCRYPTED:
            return 'lock-open'
        elif self.chat.otr_state_trust == OTR_STATE_TRUSTED:
            return 'lock-filled'
        else:
            return 'lock'


class TrustManagementButton(SymbolButton):
    pass


class EncryptionButton(BoxLayout):
    selected = properties.BooleanProperty(False)
    text = properties.StringProperty()
    trust_button = properties.BooleanProperty(False)
    best_width = properties.NumericProperty(0)
    bold = properties.BooleanProperty(True)

    def __init__(self, **kwargs):
        super(EncryptionButton, self).__init__(**kwargs)
        self.register_event_type('on_release')
        self.register_event_type('on_trust_release')
        if self.trust_button:
            self.add_widget(TrustManagementButton())

    def on_release(self):
        pass

    def on_trust_release(self):
        pass


class EncryptionMenu(DropDown):
    # best with to display all algorithms buttons + trust buttons
    best_width = properties.NumericProperty(0)

    def __init__(self, chat, **kwargs):
        """
        @param chat(Chat): Chat instance
        """
        self.chat = chat
        super(EncryptionMenu, self).__init__(**kwargs)
        btn = EncryptionButton(
            text=_("unencrypted (plain text)"),
            on_release=self.unencrypted,
            selected=True,
            bold=False,
            )
        btn.bind(
            on_release=self.unencrypted,
        )
        self.add_widget(btn)
        for plugin in G.host.encryption_plugins:
            if chat.type == C.CHAT_GROUP and plugin["directed"]:
                # directed plugins can't work with group chat
                continue
            btn = EncryptionButton(
                text=plugin['name'],
                trust_button=True,
                )
            btn.bind(
                on_release=partial(self.startEncryption, plugin=plugin),
                on_trust_release=partial(self.getTrustUI, plugin=plugin),
            )
            self.add_widget(btn)
            log.info("added encryption: {}".format(plugin['name']))

    def messageEncryptionStopCb(self):
        log.info(_("Session with {destinee} is now in plain text").format(
            destinee = self.chat.target))

    def messageEncryptionStopEb(self, failure_):
        msg = _("Error while stopping encryption with {destinee}: {reason}").format(
            destinee = self.chat.target,
            reason = failure_)
        log.warning(msg)
        G.host.addNote(_("encryption problem"), msg, C.XMLUI_DATA_LVL_ERROR)

    def unencrypted(self, button):
        self.dismiss()
        G.host.bridge.messageEncryptionStop(
            str(self.chat.target),
            self.chat.profile,
            callback=self.messageEncryptionStopCb,
            errback=self.messageEncryptionStopEb)

    def messageEncryptionStartCb(self, plugin):
        log.info(_("Session with {destinee} is now encrypted with {encr_name}").format(
            destinee = self.chat.target,
            encr_name = plugin['name']))

    def messageEncryptionStartEb(self, failure_):
        msg = _("Session can't be encrypted with {destinee}: {reason}").format(
            destinee = self.chat.target,
            reason = failure_)
        log.warning(msg)
        G.host.addNote(_("encryption problem"), msg, C.XMLUI_DATA_LVL_ERROR)

    def startEncryption(self, button, plugin):
        """Request encryption with given plugin for this session

        @param button(EncryptionButton): button which has been pressed
        @param plugin(dict): plugin data
        """
        self.dismiss()
        G.host.bridge.messageEncryptionStart(
            str(self.chat.target),
            plugin['namespace'],
            True,
            self.chat.profile,
            callback=partial(self.messageEncryptionStartCb, plugin=plugin),
            errback=self.messageEncryptionStartEb)

    def encryptionTrustUIGetCb(self, xmlui_raw):
        xml_ui = xmlui.create(
            G.host, xmlui_raw, profile=self.chat.profile)
        xml_ui.show()

    def encryptionTrustUIGetEb(self, failure_):
        msg = _("Trust manager interface can't be retrieved: {reason}").format(
            reason = failure_)
        log.warning(msg)
        G.host.addNote(_("encryption trust management problem"), msg,
                       C.XMLUI_DATA_LVL_ERROR)

    def getTrustUI(self, button, plugin):
        """Request and display trust management UI

        @param button(EncryptionButton): button which has been pressed
        @param plugin(dict): plugin data
        """
        self.dismiss()
        G.host.bridge.encryptionTrustUIGet(
            str(self.chat.target),
            plugin['namespace'],
            self.chat.profile,
            callback=self.encryptionTrustUIGetCb,
            errback=self.encryptionTrustUIGetEb)


class Chat(quick_chat.QuickChat, cagou_widget.CagouWidget):
    message_input = properties.ObjectProperty()
    messages_widget = properties.ObjectProperty()
    history_scroll = properties.ObjectProperty()
    attachments_to_send = properties.ObjectProperty()
    send_button_visible = properties.BooleanProperty()
    use_header_input = True
    global_screen_manager = True
    collection_carousel = True

    def __init__(self, host, target, type_=C.CHAT_ONE2ONE, nick=None, occupants=None,
                 subject=None, statuses=None, profiles=None):
        self.show_chat_selector = False
        if statuses is None:
            statuses = {}
        quick_chat.QuickChat.__init__(
            self, host, target, type_, nick, occupants, subject, statuses,
            profiles=profiles)
        self.otr_state_encryption = OTR_STATE_UNENCRYPTED
        self.otr_state_trust = OTR_STATE_UNTRUSTED
        # completion attributes
        self._hi_comp_data = None
        self._hi_comp_last = None
        self._hi_comp_dropdown = DropDown()
        self._hi_comp_allowed = True
        cagou_widget.CagouWidget.__init__(self)
        transfer_btn = TransferButton(chat=self)
        self.headerInputAddExtra(transfer_btn)
        if (type_ == C.CHAT_ONE2ONE or "REALJID_PUBLIC" in statuses):
            self.encryption_btn = EncryptionMainButton(self)
            self.headerInputAddExtra(self.encryption_btn)
        self.extra_menu = ExtraMenu(chat=self)
        extra_btn = ExtraButton(chat=self)
        self.headerInputAddExtra(extra_btn)
        self.header_input.hint_text = target
        self._history_prepend_lock = False
        self.history_count = 0

    def on_kv_post(self, __):
        self.postInit()

    def screenManagerInit(self, screen_manager):
        screen_manager.transition = screenmanager.SlideTransition(direction='down')
        sel_screen = Screen(name='chat_selector')
        chat_selector = ChatSelector(profile=self.profile)
        sel_screen.add_widget(chat_selector)
        screen_manager.add_widget(sel_screen)
        if self.show_chat_selector:
            transition = screen_manager.transition
            screen_manager.transition = NoTransition()
            screen_manager.current = 'chat_selector'
            screen_manager.transition = transition

    def __str__(self):
        return "Chat({})".format(self.target)

    def __repr__(self):
        return self.__str__()

    @classmethod
    def factory(cls, plugin_info, target, profiles):
        profiles = list(profiles)
        if len(profiles) > 1:
            raise NotImplementedError("Multi-profiles is not available yet for chat")
        if target is None:
            show_chat_selector = True
            target = G.host.profiles[profiles[0]].whoami
        else:
            show_chat_selector = False
        wid = G.host.widgets.getOrCreateWidget(cls, target, on_new_widget=None,
                                               on_existing_widget=G.host.getOrClone,
                                               profiles=profiles)
        wid.show_chat_selector = show_chat_selector
        return wid

    @property
    def message_widgets_rev(self):
        return self.messages_widget.children

    ## keyboard ##

    def key_input(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            screen_manager = self.screen_manager
            screen_manager.transition.direction = 'down'
            screen_manager.current = 'chat_selector'
            return True

    ## drop ##

    def on_drop_file(self, path):
        self.addAttachment(path)

    ## header ##

    def changeWidget(self, jid_):
        """change current widget for a new one with given jid

        @param jid_(jid.JID): jid of the widget to create
        """
        plugin_info = G.host.getPluginInfo(main=Chat)
        factory = plugin_info['factory']
        G.host.switchWidget(self, factory(plugin_info, jid_, profiles=[self.profile]))
        self.header_input.text = ''

    def onHeaderInput(self):
        text = self.header_input.text.strip()
        try:
            if text.count('@') != 1 or text.count(' '):
                raise ValueError
            jid_ = jid.JID(text)
        except ValueError:
            log.info("entered text is not a jid")
            return

        def discoCb(disco):
            # TODO: check if plugin XEP-0045 is activated
            if "conference" in [i[0] for i in disco[1]]:
                G.host.bridge.mucJoin(str(jid_), "", "", self.profile,
                                      callback=self._mucJoinCb, errback=self._mucJoinEb)
            else:
                self.changeWidget(jid_)

        def discoEb(failure):
            log.warning("Disco failure, ignore this text: {}".format(failure))

        G.host.bridge.discoInfos(
            jid_.domain,
            profile_key=self.profile,
            callback=discoCb,
            errback=discoEb)

    def onHeaderInputCompleted(self, input_wid, completed_text):
        self._hi_comp_allowed = False
        input_wid.text = completed_text
        self._hi_comp_allowed = True
        self._hi_comp_dropdown.dismiss()
        self.onHeaderInput()

    def onHeaderInputComplete(self, wid, text):
        if not self._hi_comp_allowed:
            return
        text = text.lstrip()
        if not text:
            self._hi_comp_data = None
            self._hi_comp_last = None
            self._hi_comp_dropdown.dismiss()
            return

        profile = list(self.profiles)[0]

        if self._hi_comp_data is None:
            # first completion, we build the initial list
            comp_data = self._hi_comp_data = []
            self._hi_comp_last = ''
            for jid_, jid_data in G.host.contact_lists[profile].all_iter:
                comp_data.append((jid_, jid_data))
            comp_data.sort(key=lambda datum: datum[0])
        else:
            comp_data = self._hi_comp_data

        # XXX: dropdown is rebuilt each time backspace is pressed or if the text is changed,
        #      it works OK, but some optimisation may be done here
        dropdown = self._hi_comp_dropdown

        if not text.startswith(self._hi_comp_last) or not self._hi_comp_last:
            # text has changed or backspace has been pressed, we restart
            dropdown.clear_widgets()

            for jid_, jid_data in comp_data:
                nick = jid_data.get('nick', '')
                if text in jid_.bare or text in nick.lower():
                    btn = JidButton(
                        jid = jid_.bare,
                        profile = profile,
                        size_hint = (0.5, None),
                        nick = nick,
                        on_release=lambda __, txt=jid_.bare: self.onHeaderInputCompleted(wid, txt)
                        )
                    dropdown.add_widget(btn)
        else:
            # more chars, we continue completion by removing unwanted widgets
            to_remove = []
            for c in dropdown.children[0].children:
                if text not in c.jid and text not in (c.nick or ''):
                    to_remove.append(c)
            for c in to_remove:
                dropdown.remove_widget(c)
        if dropdown.attach_to is None:
            dropdown.open(wid)
        self._hi_comp_last = text

    def messageDataConverter(self, idx, mess_id):
        return {"mess_data": self.messages[mess_id]}

    def _onHistoryPrinted(self):
        """Refresh or scroll down the focus after the history is printed"""
        # self.adapter.data = self.messages
        for mess_data in self.messages.values():
            self.appendMessage(mess_data)
        super(Chat, self)._onHistoryPrinted()

    def createMessage(self, message):
        self.appendMessage(message)
        # we need to render immediatly next 2 layouts to avoid an unpleasant flickering
        # when sending or receiving a message
        self.messages_widget.dont_delay_next_layouts = 2

    def appendMessage(self, mess_data):
        """Append a message Widget to the history

        @param mess_data(quick_chat.Message): message data
        """
        if self.handleUserMoved(mess_data):
            return
        self.messages_widget.add_widget(MessageWidget(mess_data=mess_data))
        self.notify(mess_data)

    def prependMessage(self, mess_data):
        """Prepend a message Widget to the history

        @param mess_data(quick_chat.Message): message data
        """
        mess_wid = self.messages_widget
        last_idx = len(mess_wid.children)
        mess_wid.add_widget(MessageWidget(mess_data=mess_data), index=last_idx)

    def _get_notif_msg(self, mess_data):
        return _("{nick}: {message}").format(
            nick=mess_data.nick,
            message=mess_data.main_message)

    def notify(self, mess_data):
        """Notify user when suitable

        For one2one chat, notification will happen when window has not focus
        or when one2one chat is not visible. A note is also there when widget
        is not visible.
        For group chat, note will be added on mention, with a desktop notification if
        window has not focus or is not visible.
        """
        visible_clones = [w for w in G.host.getVisibleList(self.__class__)
                          if w.target == self.target]
        if len(visible_clones) > 1 and visible_clones.index(self) > 0:
            # to avoid multiple notifications in case of multiple cloned widgets
            # we only handle first clone
            return
        is_visible = bool(visible_clones)
        if self.type == C.CHAT_ONE2ONE:
            if (not Window.focus or not is_visible) and not mess_data.history:
                notif_msg = self._get_notif_msg(mess_data)
                G.host.notify(
                    type_=C.NOTIFY_MESSAGE,
                    entity=mess_data.from_jid,
                    message=notif_msg,
                    subject=_("private message"),
                    widget=self,
                    profile=self.profile
                )
                if not is_visible:
                    G.host.addNote(
                        _("private message"),
                        notif_msg,
                        symbol = "chat",
                        action = {
                            "action": 'chat',
                            "target": self.target,
                            "profiles": self.profiles}
                        )
        else:
            if mess_data.mention:
                notif_msg = self._get_notif_msg(mess_data)
                G.host.addNote(
                    _("mention"),
                    notif_msg,
                    symbol = "chat",
                    action = {
                        "action": 'chat',
                        "target": self.target,
                        "profiles": self.profiles}
                    )
                if not is_visible or not Window.focus:
                    subject=_("mention ({room_jid})").format(room_jid=self.target)
                    G.host.notify(
                        type_=C.NOTIFY_MENTION,
                        entity=self.target,
                        message=notif_msg,
                        subject=subject,
                        widget=self,
                        profile=self.profile
                    )

    # message input

    def _attachmentProgressCb(self, item, metadata, profile):
        item.parent.remove_widget(item)
        log.info(f"item {item.data.get('path')} uploaded successfully")

    def _attachmentProgressEb(self, item, err_msg, profile):
        item.parent.remove_widget(item)
        path = item.data.get('path')
        msg = _("item {path} could not be uploaded: {err_msg}").format(
            path=path, err_msg=err_msg)
        G.host.addNote(_("can't upload file"), msg, C.XMLUI_DATA_LVL_WARNING)
        log.warning(msg)

    def _progressGetCb(self, item, metadata):
        try:
            position = int(metadata["position"])
            size = int(metadata["size"])
        except KeyError:
            # we got empty metadata, the progression is either not yet started or
            # finished
            if item.progress:
                # if progress is already started, receiving empty metadata means
                # that progression is finished
                item.progress = 100
                return
        else:
            item.progress = position/size*100

        if item.parent is not None:
            # the item is not yet fully received, we reschedule an update
            Clock.schedule_once(
                partial(self._attachmentProgressUpdate, item),
                PROGRESS_UPDATE)

    def _attachmentProgressUpdate(self, item, __):
        G.host.bridge.progressGet(
            item.data["progress_id"],
            self.profile,
            callback=partial(self._progressGetCb, item),
            errback=G.host.errback,
        )

    def addNick(self, nick):
        """Add a nickname to message_input if suitable"""
        if (self.type == C.CHAT_GROUP and not self.message_input.text.startswith(nick)):
            self.message_input.text = f'{nick}: {self.message_input.text}'

    def onSend(self, input_widget):
        extra = {}
        for item in self.attachments_to_send.attachments.children:
            if item.sending:
                # the item is already being sent
                continue
            item.sending = True
            progress_id = item.data["progress_id"] = str(uuid.uuid4())
            attachments = extra.setdefault(C.MESS_KEY_ATTACHMENTS, [])
            attachment = {
                "path": str(item.data["path"]),
                "progress_id": progress_id,
            }
            if 'media_type' in item.data:
                attachment[C.MESS_KEY_ATTACHMENTS_MEDIA_TYPE] = item.data['media_type']

            if ((self.attachments_to_send.reduce_checkbox.active
                 and attachment.get('media_type', '').split('/')[0] == 'image')):
                attachment[C.MESS_KEY_ATTACHMENTS_RESIZE] = True

            attachments.append(attachment)

            Clock.schedule_once(
                partial(self._attachmentProgressUpdate, item),
                PROGRESS_UPDATE)

            G.host.registerProgressCbs(
                progress_id,
                callback=partial(self._attachmentProgressCb, item),
                errback=partial(self._attachmentProgressEb, item)
            )


        G.host.messageSend(
            self.target,
            # TODO: handle language
            {'': input_widget.text},
            # TODO: put this in QuickChat
            mess_type=
                C.MESS_TYPE_GROUPCHAT if self.type == C.CHAT_GROUP else C.MESS_TYPE_CHAT,
            extra=extra,
            profile_key=self.profile
            )
        input_widget.text = ''

    def _imageCheckCb(self, report_raw):
        report = data_format.deserialise(report_raw)
        if report['too_large']:
            self.attachments_to_send.show_resize=True
            self.attachments_to_send.reduce_checkbox.active=True

    def addAttachment(self, file_path, media_type=None):
        file_path = Path(file_path)
        if media_type is None:
            media_type = mimetypes.guess_type(str(file_path), strict=False)[0]
        if not self.attachments_to_send.show_resize and media_type is not None:
            # we check if the attachment is an image and if it's too large.
            # If too large, the reduce size check box will be displayed, and checked by
            # default.
            main_type = media_type.split('/')[0]
            if main_type == "image":
                G.host.bridge.imageCheck(
                    str(file_path),
                    callback=self._imageCheckCb,
                    errback=partial(
                        G.host.errback,
                        title=_("Can't check image size"),
                        message=_("Can't check image at {path}: {{msg}}").format(
                            path=file_path),
                    )
                )

        data = {
            "path": file_path,
            "name": file_path.name,
        }

        if media_type is not None:
            data['media_type'] = media_type

        self.attachments_to_send.attachments.add_widget(
            AttachmentToSendItem(data=data)
        )

    def transferFile(self, file_path, transfer_type=C.TRANSFER_UPLOAD, cleaning_cb=None):
        # FIXME: cleaning_cb is not managed
        if transfer_type == C.TRANSFER_UPLOAD:
            self.addAttachment(file_path)
        elif transfer_type == C.TRANSFER_SEND:
            if self.type == C.CHAT_GROUP:
                log.warning("P2P transfer is not possible for group chat")
                # TODO: show an error dialog to user, or better hide the send button for
                #       MUC
            else:
                jid_ = self.target
                if not jid_.resource:
                    jid_ = G.host.contact_lists[self.profile].getFullJid(jid_)
                G.host.bridge.fileSend(str(jid_), str(file_path), "", "", {},
                                       profile=self.profile)
                # TODO: notification of sending/failing
        else:
            raise log.error("transfer of type {} are not handled".format(transfer_type))

    def messageEncryptionStarted(self, plugin_data):
        quick_chat.QuickChat.messageEncryptionStarted(self, plugin_data)
        self.encryption_btn.symbol = SYMBOL_ENCRYPTED
        self.encryption_btn.color = COLOR_ENCRYPTED
        self.encryption_btn.selectAlgo(plugin_data['name'])

    def messageEncryptionStopped(self, plugin_data):
        quick_chat.QuickChat.messageEncryptionStopped(self, plugin_data)
        self.encryption_btn.symbol = SYMBOL_UNENCRYPTED
        self.encryption_btn.color = COLOR_UNENCRYPTED
        self.encryption_btn.selectAlgo(None)

    def _mucJoinCb(self, joined_data):
        joined, room_jid_s, occupants, user_nick, subject, statuses, profile = joined_data
        self.host.mucRoomJoinedHandler(*joined_data[1:])
        jid_ = jid.JID(room_jid_s)
        self.changeWidget(jid_)

    def _mucJoinEb(self, failure):
        log.warning("Can't join room: {}".format(failure))

    def onOTRState(self, state, dest_jid, profile):
        assert profile in self.profiles
        if state in OTR_STATE_ENCRYPTION:
            self.otr_state_encryption = state
        elif state in OTR_STATE_TRUST:
            self.otr_state_trust = state
        else:
            log.error(_("Unknown OTR state received: {}".format(state)))
            return
        self.encryption_btn.symbol = self.encryption_btn.getSymbol()
        self.encryption_btn.color = self.encryption_btn.getColor()

    def onVisible(self):
        if not self.sync:
            self.resync()

    def onSelected(self):
        G.host.clearNotifs(self.target, profile=self.profile)

    def onDelete(self, **kwargs):
        if kwargs.get('explicit_close', False):
            wrapper = self.whwrapper
            if wrapper is not None:
                if len(wrapper.carousel.slides) == 1:
                    # if we delete the last opened chat, we need to show the selector
                    screen_manager = self.screen_manager
                    screen_manager.transition.direction = 'down'
                    screen_manager.current = 'chat_selector'
                wrapper.carousel.remove_widget(self)
            return True
        # we always keep one widget, so it's available when swiping
        # TODO: delete all widgets when chat is closed
        nb_instances = sum(1 for _ in self.host.widgets.getWidgetInstances(self))
        # we want to keep at least one instance of Chat by WHWrapper
        nb_to_keep = len(G.host.widgets_handler.children)
        if nb_instances <= nb_to_keep:
            return False

    def _history_unlock(self, __):
        self._history_prepend_lock = False
        log.debug("history prepend unlocked")
        # we call manually onScroll, to check if we are still in the scrolling zone
        self.onScroll(self.history_scroll, self.history_scroll.scroll_y)

    def _history_scroll_adjust(self, __, scroll_start_height):
        # history scroll position must correspond to where it was before new messages
        # have been appended
        self.history_scroll.scroll_y = (
            scroll_start_height / self.messages_widget.height
        )

        # we want a small delay before unlocking, to avoid re-fetching history
        # again
        Clock.schedule_once(self._history_unlock, 1.5)

    def _backHistoryGetCb_post(self, __, history, scroll_start_height):
        if len(history) == 0:
            # we don't unlock self._history_prepend_lock if there is no history, as there
            # is no sense to try to retrieve more in this case.
            log.debug(f"we've reached top of history for {self.target.bare} chat")
        else:
            # we have to schedule again for _history_scroll_adjust, else messages_widget
            # is not resized (self.messages_widget.height is not yet updated)
            # as a result, the scroll_to can't work correctly
            Clock.schedule_once(partial(
                self._history_scroll_adjust,
                scroll_start_height=scroll_start_height))
            log.debug(
                f"{len(history)} messages prepended to history (last: {history[0][0]})")

    def _backHistoryGetCb(self, history):
        # TODO: factorise with QuickChat._historyGetCb
        scroll_start_height = self.messages_widget.height * self.history_scroll.scroll_y
        for data in reversed(history):
            uid, timestamp, from_jid, to_jid, message, subject, type_, extra_s = data
            from_jid = jid.JID(from_jid)
            to_jid = jid.JID(to_jid)
            extra = data_format.deserialise(extra_s)
            extra["history"] = True
            self.messages[uid] = message = quick_chat.Message(
                self,
                uid,
                timestamp,
                from_jid,
                to_jid,
                message,
                subject,
                type_,
                extra,
                self.profile,
            )
            self.messages.move_to_end(uid, last=False)
            self.prependMessage(message)
        Clock.schedule_once(partial(
            self._backHistoryGetCb_post,
            history=history,
            scroll_start_height=scroll_start_height))

    def _backHistoryGetEb(self, failure_):
        G.host.addNote(
            _("Problem while getting back history"),
            _("Can't back history for {target}: {problem}").format(
                target=self.target, problem=failure_),
            C.XMLUI_DATA_LVL_ERROR)
        # we don't unlock self._history_prepend_lock on purpose, no need
        # to try to get more history if something is wrong

    def onScroll(self, scroll_view, scroll_y):
        if self._history_prepend_lock:
            return
        if (1-scroll_y) * self.messages_widget.height < INFINITE_SCROLL_LIMIT:
            self._history_prepend_lock = True
            log.debug(f"Retrieving back history for {self} [{self.history_count}]")
            self.history_count += 1
            first_uid = next(iter(self.messages.keys()))
            filters = self.history_filters.copy()
            filters['before_uid'] = first_uid
            self.host.bridge.historyGet(
                str(self.host.profiles[self.profile].whoami.bare),
                str(self.target),
                30,
                True,
                {k: str(v) for k,v in filters.items()},
                self.profile,
                callback=self._backHistoryGetCb,
                errback=self._backHistoryGetEb,
            )


class ChatSelector(cagou_widget.CagouWidget, FilterBehavior):
    jid_selector = properties.ObjectProperty()
    profile = properties.StringProperty()
    plugin_info_class = Chat
    use_header_input = True

    def on_select(self, contact_button):
        contact_jid = jid.JID(contact_button.jid)
        plugin_info = G.host.getPluginInfo(main=Chat)
        factory = plugin_info['factory']
        self.screen_manager.transition.direction = 'up'
        carousel = self.whwrapper.carousel
        current_slides = {w.target: w for w in carousel.slides}
        if contact_jid in current_slides:
            slide = current_slides[contact_jid]
            idx = carousel.slides.index(slide)
            carousel.index = idx
            self.screen_manager.current = ''
        else:
            G.host.switchWidget(
                self, factory(plugin_info, contact_jid, profiles=[self.profile]))


    def onHeaderInput(self):
        text = self.header_input.text.strip()
        try:
            if text.count('@') != 1 or text.count(' '):
                raise ValueError
            jid_ = jid.JID(text)
        except ValueError:
            log.info("entered text is not a jid")
            return
        G.host.doAction("chat", jid_, [self.profile])

    def onHeaderInputComplete(self, wid, text, **kwargs):
        """we filter items when text is entered in input box"""
        for layout in self.jid_selector.items_layouts:
            self.do_filter(
                layout,
                text,
                # we append nick to jid to filter on both
                lambda c: c.jid + c.data.get('nick', ''),
                width_cb=lambda c: c.base_width,
                height_cb=lambda c: c.minimum_height,
                continue_tests=[lambda c: not isinstance(c, ContactButton)])


PLUGIN_INFO["factory"] = Chat.factory
quick_widgets.register(quick_chat.QuickChat, Chat)
