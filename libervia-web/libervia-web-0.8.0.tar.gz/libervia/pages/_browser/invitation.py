from browser import document, window, timer
from bridge import Bridge
from template import Template
import dialog
from cache import cache
import javascript

bridge = Bridge()
# we use JS RegExp because Python's re is really long to import in Brython
# FIXME: this is a naive JID regex, a more accurate should be used instead
jid_re = javascript.RegExp.new(r"^\w+@\w+\.\w+")


class InvitationManager:

    def __init__(self, invitation_type, invitation_data):
        self.invitation_type = invitation_type
        self.invitation_data = invitation_data
        manager_panel_tpl = Template('invitation/manager.html')
        self.manager_panel_elt = manager_panel_tpl.get_elt()
        self.invite_by_email_tpl = Template('invitation/invite_by_email.html')
        self.affiliation_tpl = Template('invitation/affiliation_item.html')
        self.new_item_tpl = Template('invitation/new_item.html')
        # list of item passing filter when adding a new contact
        self._filtered_new_items = {}
        self._active_new_item = None
        self._idx = 0

    def attach(self, affiliations=None):
        if affiliations is None:
            affiliations = {}
        self.affiliations = affiliations
        self.side_panel = self.manager_panel_elt.select_one(
            '.invitation_manager_side_panel')
        self.open()
        for close_elt in self.manager_panel_elt.select('.click_to_close'):
            close_elt.bind("click", self.on_manager_close)
        self.side_panel.bind("click", lambda evt: evt.stopPropagation())

        cache.fill_identities(affiliations.keys(), callback=self._set_affiliations)

        contact_elt = self.manager_panel_elt.select_one('input[name="contact"]')
        contact_elt.bind("input", self.on_contact_input)
        contact_elt.bind("keydown", self.on_contact_keydown)
        contact_elt.bind("focus", self.on_contact_focus)
        contact_elt.bind("blur", self.on_contact_blur)
        document['invite_email'].bind('click', self.on_invite_email_click)

    def _set_affiliations(self):
        for entity_jid, affiliation in self.affiliations.items():
            self.set_affiliation(entity_jid, affiliation)

    def open(self):
        """Re-attach and show a closed panel"""
        self._body_ori_style = document.body.style.height, document.body.style.overflow
        document.body.style.height = '100vh'
        document.body.style.overflow = 'hidden'
        document.body <= self.manager_panel_elt
        timer.set_timeout(lambda: self.side_panel.classList.add("open"), 0)

    def _on_close_transition_end(self, evt):
        self.manager_panel_elt.remove()
        # FIXME: not working with Brython, to report upstream
        # self.side_panel.unbind("transitionend", self._on_close_transition_end)
        self.side_panel.unbind("transitionend")

    def close(self):
        """Hide the panel"""
        document.body.style.height, document.body.style.overflow = self._body_ori_style
        self.side_panel.classList.remove('open')
        self.side_panel.bind("transitionend", self._on_close_transition_end)

    def _invite_jid(self, entity_jid, callback, errback=None):
        if errback is None:
            errback = lambda e: dialog.notification.show(f"invitation failed: {e}", "error")
        if self.invitation_type == 'photos':
            service = self.invitation_data["service"]
            path = self.invitation_data["path"]
            album_name = path.rsplit('/')[-1]
            print(f"inviting {entity_jid}")
            bridge.FISInvite(
                entity_jid,
                service,
                "photos",
                "",
                path,
                album_name,
                '',
                callback=callback,
                errback=errback
            )
        elif self.invitation_type == 'pubsub':
            service = self.invitation_data["service"]
            node = self.invitation_data["node"]
            name = self.invitation_data.get("name")
            namespace = self.invitation_data.get("namespace")
            extra = {}
            if namespace:
                extra["namespace"] = namespace
            print(f"inviting {entity_jid}")
            bridge.psInvite(
                entity_jid,
                service,
                node,
                '',
                name,
                javascript.JSON.stringify(extra),
                callback=callback,
                errback=errback
            )
        else:
            print(f"error: unknown invitation type: {self.invitation_type}")

    def invite_by_jid(self, entity_jid):
        self._invite_jid(
            entity_jid,
            callback=lambda entity_jid=entity_jid: self._on_jid_invitation_success(entity_jid),
        )

    def on_manager_close(self, evt):
        self.close()

    def _on_jid_invitation_success(self, entity_jid):
        form_elt = document['invitation_form']
        contact_elt = form_elt.select_one('input[name="contact"]')
        contact_elt.value = ""
        contact_elt.dispatchEvent(window.Event.new('input'))
        dialog.notification.show(
            f"{entity_jid} has been invited",
            level="success",
        )
        if entity_jid not in self.affiliations:
            self.set_affiliation(entity_jid, "member")

    def on_contact_invite(self, evt, entity_jid):
        """User is adding a contact"""
        form_elt = document['invitation_form']
        contact_elt = form_elt.select_one('input[name="contact"]')
        contact_elt.value = ""
        contact_elt.dispatchEvent(window.Event.new('input'))
        self.invite_by_jid(entity_jid)

    def on_contact_keydown(self, evt):
        if evt.key == "Escape":
            evt.target.value = ""
            evt.target.dispatchEvent(window.Event.new('input'))
        elif evt.key == "ArrowDown":
            evt.stopPropagation()
            evt.preventDefault()
            content_elt = document['invitation_contact_search'].select_one(
                ".search_dialog__content")
            if self._active_new_item == None:
                self._active_new_item = content_elt.firstElementChild
                self._active_new_item.classList.add('selected')
            else:
                next_item = self._active_new_item.nextElementSibling
                if next_item is not None:
                    self._active_new_item.classList.remove('selected')
                    self._active_new_item = next_item
                    self._active_new_item.classList.add('selected')
        elif evt.key == "ArrowUp":
            evt.stopPropagation()
            evt.preventDefault()
            content_elt = document['invitation_contact_search'].select_one(
                ".search_dialog__content")
            if self._active_new_item == None:
                self._active_new_item = content_elt.lastElementChild
                self._active_new_item.classList.add('selected')
            else:
                previous_item = self._active_new_item.previousElementSibling
                if previous_item is not None:
                    self._active_new_item.classList.remove('selected')
                    self._active_new_item = previous_item
                    self._active_new_item.classList.add('selected')
        elif evt.key == "Enter":
            evt.stopPropagation()
            evt.preventDefault()
            if self._active_new_item is not None:
                entity_jid = self._active_new_item.dataset.entityJid
                self.invite_by_jid(entity_jid)
            else:
                if jid_re.exec(evt.target.value):
                    self.invite_by_jid(evt.target.value)
                    evt.target.value = ""

    def on_contact_focus(self, evt):
        search_dialog = document['invitation_contact_search']
        search_dialog.classList.add('open')
        self._active_new_item = None
        evt.target.dispatchEvent(window.Event.new('input'))

    def on_contact_blur(self, evt):
        search_dialog = document['invitation_contact_search']
        search_dialog.classList.remove('open')
        for elt in self._filtered_new_items.values():
            elt.remove()
        self._filtered_new_items.clear()


    def on_contact_input(self, evt):
        text = evt.target.value.strip().lower()
        search_dialog = document['invitation_contact_search']
        content_elt = search_dialog.select_one(".search_dialog__content")
        for (entity_jid, identity) in cache.identities.items():
            if not cache.match_identity(entity_jid, text, identity):
                # if the entity was present in last pass, we remove it
                try:
                    filtered_item = self._filtered_new_items.pop(entity_jid)
                except KeyError:
                    pass
                else:
                    filtered_item.remove()
                continue
            if entity_jid not in self._filtered_new_items:
                # we only create a new element if the item was not already there
                new_item_elt = self.new_item_tpl.get_elt({
                    "entity_jid": entity_jid,
                    "identities": cache.identities,
                })
                content_elt <= new_item_elt
                self._filtered_new_items[entity_jid] = new_item_elt
                for elt in new_item_elt.select('.click_to_ok'):
                    # we use mousedown instead of click because otherwise it would be
                    # ignored due to "blur" event manager (see
                    # https://stackoverflow.com/a/9335401)
                    elt.bind(
                        "mousedown",
                        lambda evt, entity_jid=entity_jid: self.on_contact_invite(
                            evt, entity_jid),
                    )

        if ((self._active_new_item is not None
             and not self._active_new_item.parentElement)):
            # active item has been filtered out
            self._active_new_item = None

    def _on_email_invitation_success(self, invitee_jid, email, name):
        self.set_affiliation(invitee_jid, "member")
        dialog.notification.show(
            f"{name} has been invited, he/she has received an email with a link",
            level="success",
        )

    def invitationSimpleCreateCb(self, invitation_data, email, name):
        invitee_jid = invitation_data['jid']
        self._invite_jid(
            invitee_jid,
            callback=lambda: self._on_email_invitation_success(invitee_jid, email, name),
            errback=lambda e: dialog.notification.show(
                f"invitation failed for {email}: {e}",
                "error"
            )
        )

        # we update identities to have the name instead of the invitation jid in
        # affiliations
        cache.identities[invitee_jid] = {'nicknames': [name]}
        cache.update()

    def invite_by_email(self, email, name):
        guest_url_tpl = f'{window.URL.new("/g", document.baseURI).href}/{{uuid}}'
        bridge.invitationSimpleCreate(
            email,
            name,
            guest_url_tpl,
            '',
            callback=lambda data: self.invitationSimpleCreateCb(data, email, name),
            errback=lambda e: window.alert(f"can't send email invitation: {e}")
        )

    def on_invite_email_submit(self, evt, invite_email_elt):
        evt.stopPropagation()
        evt.preventDefault()
        form = document['email_invitation_form']
        try:
            reportValidity = form.reportValidity
        except AttributeError:
            print("reportValidity is not supported by this browser!")
        else:
            if not reportValidity():
                return
        email = form.select_one('input[name="email"]').value
        name = form.select_one('input[name="name"]').value
        self.invite_by_email(email, name)
        invite_email_elt.remove()
        self.open()

    def on_invite_email_close(self, evt, invite_email_elt):
        evt.stopPropagation()
        evt.preventDefault()
        invite_email_elt.remove()
        self.open()

    def on_invite_email_click(self, evt):
        evt.stopPropagation()
        evt.preventDefault()
        invite_email_elt = self.invite_by_email_tpl.get_elt()
        document.body <= invite_email_elt
        document['email_invitation_submit'].bind(
            'click', lambda evt: self.on_invite_email_submit(evt, invite_email_elt)
        )
        for close_elt in invite_email_elt.select('.click_to_close'):
            close_elt.bind(
                "click", lambda evt: self.on_invite_email_close(evt, invite_email_elt))
        self.close()

    ## affiliations

    def _addAffiliationBindings(self, entity_jid, affiliation_elt):
        for elt in affiliation_elt.select(".click_to_delete"):
            elt.bind(
                "click",
                lambda evt, entity_jid=entity_jid, affiliation_elt=affiliation_elt:
                self.on_affiliation_remove(entity_jid, affiliation_elt)
            )
        for elt in affiliation_elt.select(".click_to_set_publisher"):
            try:
                name = cache.identities[entity_jid]["nicknames"][0]
            except (KeyError, IndexError):
                name = entity_jid
            elt.bind(
                "click",
                lambda evt, entity_jid=entity_jid, name=name,
                    affiliation_elt=affiliation_elt:
                    self.on_affiliation_set(
                        entity_jid, name, affiliation_elt, "publisher"
                    ),
            )
        for elt in affiliation_elt.select(".click_to_set_member"):
            try:
                name = cache.identities[entity_jid]["nicknames"][0]
            except (KeyError, IndexError):
                name = entity_jid
            elt.bind(
                "click",
                lambda evt, entity_jid=entity_jid, name=name,
                    affiliation_elt=affiliation_elt:
                    self.on_affiliation_set(
                        entity_jid, name, affiliation_elt, "member"
                    ),
            )

    def set_affiliation(self, entity_jid, affiliation):
        if affiliation not in ('owner', 'member', 'publisher'):
            raise NotImplementedError(
                f'{affiliation} affiliation can not be set with this method for the '
                'moment')
        if entity_jid not in self.affiliations:
            self.affiliations[entity_jid] = affiliation
        affiliation_elt = self.affiliation_tpl.get_elt({
            "entity_jid": entity_jid,
            "affiliation": affiliation,
            "identities": cache.identities,
        })
        document['affiliations'] <= affiliation_elt
        self._addAffiliationBindings(entity_jid, affiliation_elt)

    def _on_affiliation_remove_success(self, affiliation_elt, entity_jid):
        affiliation_elt.remove()
        del self.affiliations[entity_jid]

    def on_affiliation_remove(self, entity_jid, affiliation_elt):
        if self.invitation_type == 'photos':
            path = self.invitation_data["path"]
            service = self.invitation_data["service"]
            bridge.FISAffiliationsSet(
                service,
                "",
                path,
                {entity_jid: "none"},
                callback=lambda: self._on_affiliation_remove_success(
                    affiliation_elt, entity_jid),
                errback=lambda e: dialog.notification.show(
                    f"can't remove affiliation: {e}", "error")
            )
        elif self.invitation_type == 'pubsub':
            service = self.invitation_data["service"]
            node = self.invitation_data["node"]
            bridge.psNodeAffiliationsSet(
                service,
                node,
                {entity_jid: "none"},
                callback=lambda: self._on_affiliation_remove_success(
                    affiliation_elt, entity_jid),
                errback=lambda e: dialog.notification.show(
                    f"can't remove affiliation: {e}", "error")
            )
        else:
            dialog.notification.show(
                f"error: unknown invitation type: {self.invitation_type}",
                "error"
            )

    def _on_affiliation_set_success(self, entity_jid, name, affiliation_elt, affiliation):
        dialog.notification.show(f"permission updated for {name}")
        self.affiliations[entity_jid] = affiliation
        new_affiliation_elt = self.affiliation_tpl.get_elt({
            "entity_jid": entity_jid,
            "affiliation": affiliation,
            "identities": cache.identities,
        })
        affiliation_elt.replaceWith(new_affiliation_elt)
        self._addAffiliationBindings(entity_jid, new_affiliation_elt)

    def _on_affiliation_set_ok(self, entity_jid, name, affiliation_elt, affiliation):
        if self.invitation_type == 'pubsub':
            service = self.invitation_data["service"]
            node = self.invitation_data["node"]
            bridge.psNodeAffiliationsSet(
                service,
                node,
                {entity_jid: affiliation},
                callback=lambda: self._on_affiliation_set_success(
                    entity_jid, name, affiliation_elt, affiliation
                ),
                errback=lambda e: dialog.notification.show(
                    f"can't set affiliation: {e}", "error")
            )
        else:
            dialog.notification.show(
                f"error: unknown invitation type: {self.invitation_type}",
                "error"
            )

    def _on_affiliation_set_cancel(self, evt, notif_elt):
        notif_elt.remove()
        self.open()

    def on_affiliation_set(self, entity_jid, name, affiliation_elt, affiliation):
        if affiliation == "publisher":
            message = f"Give autorisation to publish to {name}?"
        elif affiliation == "member":
            message = f"Remove autorisation to publish from {name}?"
        else:
            dialog.notification.show(f"unmanaged affiliation: {affiliation}", "error")
            return
        dialog.Confirm(message).show(
            ok_cb=lambda evt, notif_elt:
                self._on_affiliation_set_ok(
                    entity_jid, name, affiliation_elt, affiliation
                ),
            cancel_cb=self._on_affiliation_set_cancel
        )
        self.close()
