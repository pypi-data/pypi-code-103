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
import bisect
import re
from sat.core import log as logging
from sat.core.i18n import _
from sat_frontends.quick_frontend.quick_contact_list import QuickContactList
from sat_frontends.tools import jid
from kivy import properties
from cagou import G
from ..core import cagou_widget
from ..core.constants import Const as C
from ..core.common import ContactItem
from ..core.behaviors import FilterBehavior, TouchMenuBehavior, TouchMenuItemBehavior
from ..core.menu import SideMenu


log = logging.getLogger(__name__)


PLUGIN_INFO = {
    "name": _("contacts"),
    "main": "ContactList",
    "description": _("list of contacts"),
    "icon_medium": "{media}/icons/muchoslava/png/contact_list_no_border_blue_44.png"
}


class AddContactMenu(SideMenu):
    profile = properties.StringProperty()
    size_hint_close = (1, 0)
    size_hint_open = (1, 0.5)

    def __init__(self, **kwargs):
        super(AddContactMenu, self).__init__(**kwargs)
        if self.profile is None:
            log.warning(_("profile not set in AddContactMenu"))
            self.profile = next(iter(G.host.profiles))

    def addContact(self, contact_jid):
        """Actually add the contact

        @param contact_jid(unicode): jid of the contact to add
        """
        self.hide()
        contact_jid = contact_jid.strip()
        # FIXME: trivial jid verification
        if not contact_jid or not re.match(r"[^@ ]+@[^@ ]+", contact_jid):
            return
        contact_jid = jid.JID(contact_jid).bare
        G.host.bridge.addContact(str(contact_jid),
            self.profile,
            callback=lambda: G.host.addNote(
                _("contact request"),
                _("a contact request has been sent to {contact_jid}").format(
                    contact_jid=contact_jid)),
            errback=partial(G.host.errback,
                title=_("can't add contact"),
                message=_("error while trying to add contact: {msg}")))


class DelContactMenu(SideMenu):
    size_hint_close = (1, 0)
    size_hint_open = (1, 0.5)

    def __init__(self, contact_item, **kwargs):
        self.contact_item = contact_item
        super(DelContactMenu, self).__init__(**kwargs)

    def do_delete_contact(self):
        self.hide()
        G.host.bridge.delContact(str(self.contact_item.jid.bare),
        self.contact_item.profile,
        callback=lambda: G.host.addNote(
            _("contact removed"),
            _("{contact_jid} has been removed from your contacts list").format(
                contact_jid=self.contact_item.jid.bare)),
        errback=partial(G.host.errback,
            title=_("can't remove contact"),
            message=_("error while trying to remove contact: {msg}")))


class CLContactItem(TouchMenuItemBehavior, ContactItem):

    def do_item_action(self, touch):
        assert self.profile
        # XXX: for now clicking on an item launch the corresponding Chat widget
        #      behaviour should change in the future
        G.host.doAction('chat', jid.JID(self.jid), [self.profile])

    def getMenuChoices(self):
        choices = []
        choices.append(dict(text=_('delete'),
                            index=len(choices)+1,
                            callback=self.main_wid.removeContact))
        return choices


class ContactList(QuickContactList, cagou_widget.CagouWidget, FilterBehavior,
                  TouchMenuBehavior):
    float_layout = properties.ObjectProperty()
    layout = properties.ObjectProperty()
    use_header_input = True

    def __init__(self, host, target, profiles):
        QuickContactList.__init__(self, G.host, profiles)
        cagou_widget.CagouWidget.__init__(self)
        FilterBehavior.__init__(self)
        self._wid_map = {}  # (profile, bare_jid) to widget map
        self.postInit()
        if len(self.profiles) != 1:
            raise NotImplementedError('multi profiles is not implemented yet')
        self.update(profile=next(iter(self.profiles)))

    def addContactMenu(self):
        """Show the "add a contact" menu"""
        # FIXME: for now we add contact to the first profile we find
        profile = next(iter(self.profiles))
        AddContactMenu(profile=profile).show()

    def removeContact(self, menu_label):
        item = self.menu_item
        self.clear_menu()
        DelContactMenu(contact_item=item).show()

    def onHeaderInputComplete(self, wid, text):
        self.do_filter(self.layout,
                       text,
                       lambda c: c.jid,
                       width_cb=lambda c: c.base_width,
                       height_cb=lambda c: c.minimum_height,
                       )

    def _addContactItem(self, bare_jid, profile):
        """Create a new CLContactItem instance, and add it

        item will be added in a sorted position
        @param bare_jid(jid.JID): entity bare JID
        @param profile(unicode): profile where the contact is
        """
        data = G.host.contact_lists[profile].getItem(bare_jid)
        wid = CLContactItem(profile=profile, data=data, jid=bare_jid, main_wid=self)
        child_jids = [c.jid for c in reversed(self.layout.children)]
        idx = bisect.bisect_right(child_jids, bare_jid)
        self.layout.add_widget(wid, -idx)
        self._wid_map[(profile, bare_jid)] = wid

    def update(self, entities=None, type_=None, profile=None):
        log.debug("update: %s %s %s" % (entities, type_, profile))
        if type_ == None or type_ == C.UPDATE_STRUCTURE:
            log.debug("full contact list update")
            self.layout.clear_widgets()
            for bare_jid, data in self.items_sorted.items():
                wid = CLContactItem(
                    profile=data['profile'],
                    data=data,
                    jid=bare_jid,
                    main_wid=self,
                )
                self.layout.add_widget(wid)
                self._wid_map[(profile, bare_jid)] = wid
        elif type_ == C.UPDATE_MODIFY:
            for entity in entities:
                entity_bare = entity.bare
                wid = self._wid_map[(profile, entity_bare)]
                wid.data = G.host.contact_lists[profile].getItem(entity_bare)
        elif type_ == C.UPDATE_ADD:
            for entity in entities:
                self._addContactItem(entity.bare, profile)
        elif type_ == C.UPDATE_DELETE:
            for entity in entities:
                try:
                    self.layout.remove_widget(self._wid_map.pop((profile, entity.bare)))
                except KeyError:
                    log.debug("entity not found: {entity}".format(entity=entity.bare))
        else:
            log.debug("update type not handled: {update_type}".format(update_type=type_))
