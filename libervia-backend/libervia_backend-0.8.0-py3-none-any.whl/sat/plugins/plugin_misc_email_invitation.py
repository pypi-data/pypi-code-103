#!/usr/bin/env python3

# SàT plugin for sending invitations by email
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

import shortuuid
from typing import Optional
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber import error
from twisted.words.protocols.jabber import sasl
from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core import exceptions
from sat.core.log import getLogger
from sat.tools import utils
from sat.tools.common import data_format
from sat.memory import persistent
from sat.tools.common import email as sat_email

log = getLogger(__name__)


PLUGIN_INFO = {
    C.PI_NAME: "Email Invitations",
    C.PI_IMPORT_NAME: "EMAIL_INVITATION",
    C.PI_TYPE: C.PLUG_TYPE_MISC,
    C.PI_DEPENDENCIES: ['XEP-0077'],
    C.PI_RECOMMENDATIONS: ["IDENTITY"],
    C.PI_MAIN: "InvitationsPlugin",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""invitation of people without XMPP account""")
}


SUFFIX_MAX = 5
INVITEE_PROFILE_TPL = "guest@@{uuid}"
KEY_ID = 'id'
KEY_JID = 'jid'
KEY_CREATED = 'created'
KEY_LAST_CONNECTION = 'last_connection'
KEY_GUEST_PROFILE = 'guest_profile'
KEY_PASSWORD = 'password'
KEY_EMAILS_EXTRA = 'emails_extra'
EXTRA_RESERVED = {KEY_ID, KEY_JID, KEY_CREATED, 'jid_', 'jid', KEY_LAST_CONNECTION,
                  KEY_GUEST_PROFILE, KEY_PASSWORD, KEY_EMAILS_EXTRA}
DEFAULT_SUBJECT = D_("You have been invited by {host_name} to {app_name}")
DEFAULT_BODY = D_("""Hello {name}!

You have received an invitation from {host_name} to participate to "{app_name}".
To join, you just have to click on the following URL:
{url}

Please note that this URL should not be shared with anybody!
If you want more details on {app_name}, you can check {app_url}.

Welcome!
""")


class InvitationsPlugin(object):

    def __init__(self, host):
        log.info(_("plugin Invitations initialization"))
        self.host = host
        self.invitations = persistent.LazyPersistentBinaryDict('invitations')
        host.bridge.addMethod("invitationCreate", ".plugin", in_sign='sasssssssssa{ss}s',
                              out_sign='a{ss}',
                              method=self._create,
                              async_=True)
        host.bridge.addMethod("invitationGet", ".plugin", in_sign='s', out_sign='a{ss}',
                              method=self.get,
                              async_=True)
        host.bridge.addMethod("invitationDelete", ".plugin", in_sign='s', out_sign='',
                              method=self._delete,
                              async_=True)
        host.bridge.addMethod("invitationModify", ".plugin", in_sign='sa{ss}b',
                              out_sign='',
                              method=self._modify,
                              async_=True)
        host.bridge.addMethod("invitationList", ".plugin", in_sign='s',
                              out_sign='a{sa{ss}}',
                              method=self._list,
                              async_=True)
        host.bridge.addMethod("invitationSimpleCreate", ".plugin", in_sign='sssss',
                              out_sign='a{ss}',
                              method=self._simpleCreate,
                              async_=True)

    def checkExtra(self, extra):
        if EXTRA_RESERVED.intersection(extra):
            raise ValueError(
                _("You can't use following key(s) in extra, they are reserved: {}")
                .format(', '.join(EXTRA_RESERVED.intersection(extra))))

    def _create(self, email='', emails_extra=None, jid_='', password='', name='',
                host_name='', language='', url_template='', message_subject='',
                message_body='', extra=None, profile=''):
        # XXX: we don't use **kwargs here to keep arguments name for introspection with
        #      D-Bus bridge
        if emails_extra is None:
            emails_extra = []

        if extra is None:
            extra = {}
        else:
            extra = {str(k): str(v) for k,v in extra.items()}

        kwargs = {"extra": extra,
                  KEY_EMAILS_EXTRA: [str(e) for e in emails_extra]
                  }

        # we need to be sure that values are unicode, else they won't be pickled correctly
        # with D-Bus
        for key in ("jid_", "password", "name", "host_name", "email", "language",
                    "url_template", "message_subject", "message_body", "profile"):
            value = locals()[key]
            if value:
                kwargs[key] = str(value)
        return defer.ensureDeferred(self.create(**kwargs))

    async def getExistingInvitation(self, email: Optional[str]) -> Optional[dict]:
        """Retrieve existing invitation with given email

        @param email: check if any invitation exist with this email
        @return: first found invitation, or None if nothing found
        """
        # FIXME: This method is highly inefficient, it get all invitations and check them
        # one by one, this is just a temporary way to avoid creating creating new accounts
        # for an existing email. A better way will be available with Libervia 0.9.
        # TODO: use a better way to check existing invitations

        if email is None:
            return None
        all_invitations = await self.invitations.all()
        for id_, invitation in all_invitations.items():
            if invitation.get("email") == email:
                invitation[KEY_ID] = id_
                return invitation

    async def _createAccountAndProfile(
        self,
        id_: str,
        kwargs: dict,
        extra: dict
    ) -> None:
        """Create XMPP account and Libervia profile for guest"""
        ## XMPP account creation
        password = kwargs.pop('password', None)
        if password is None:
           password = utils.generatePassword()
        assert password
        # XXX: password is here saved in clear in database
        #      it is needed for invitation as the same password is used for profile
        #      and SàT need to be able to automatically open the profile with the uuid
        # FIXME: we could add an extra encryption key which would be used with the
        #        uuid when the invitee is connecting (e.g. with URL). This key would
        #        not be saved and could be used to encrypt profile password.
        extra[KEY_PASSWORD] = password

        jid_ = kwargs.pop('jid_', None)
        if not jid_:
            domain = self.host.memory.getConfig(None, 'xmpp_domain')
            if not domain:
                # TODO: fallback to profile's domain
                raise ValueError(_("You need to specify xmpp_domain in sat.conf"))
            jid_ = "invitation-{uuid}@{domain}".format(uuid=shortuuid.uuid(),
                                                        domain=domain)
        jid_ = jid.JID(jid_)
        extra[KEY_JID] = jid_.full()

        if jid_.user:
            # we don't register account if there is no user as anonymous login is then
            # used
            try:
                await self.host.plugins['XEP-0077'].registerNewAccount(jid_, password)
            except error.StanzaError as e:
                prefix = jid_.user
                idx = 0
                while e.condition == 'conflict':
                    if idx >= SUFFIX_MAX:
                        raise exceptions.ConflictError(_("Can't create XMPP account"))
                    jid_.user = prefix + '_' + str(idx)
                    log.info(_("requested jid already exists, trying with {}".format(
                        jid_.full())))
                    try:
                        await self.host.plugins['XEP-0077'].registerNewAccount(
                            jid_,
                            password
                        )
                    except error.StanzaError:
                        idx += 1
                    else:
                        break
                if e.condition != 'conflict':
                    raise e

            log.info(_("account {jid_} created").format(jid_=jid_.full()))

        ## profile creation

        extra[KEY_GUEST_PROFILE] = guest_profile = INVITEE_PROFILE_TPL.format(
            uuid=id_
        )
        # profile creation should not fail as we generate unique name ourselves
        await self.host.memory.createProfile(guest_profile, password)
        await self.host.memory.startSession(password, guest_profile)
        await self.host.memory.setParam("JabberID", jid_.full(), "Connection",
                                        profile_key=guest_profile)
        await self.host.memory.setParam("Password", password, "Connection",
                                        profile_key=guest_profile)

    async def create(self, **kwargs):
        r"""Create an invitation

        This will create an XMPP account and a profile, and use a UUID to retrieve them.
        The profile is automatically generated in the form guest@@[UUID], this way they
            can be retrieved easily
        **kwargs: keywords arguments which can have the following keys, unset values are
                  equivalent to None:
            jid_(jid.JID, None): jid to use for invitation, the jid will be created using
                                 XEP-0077
                if the jid has no user part, an anonymous account will be used (no XMPP
                    account created in this case)
                if None, automatically generate an account name (in the form
                    "invitation-[random UUID]@domain.tld") (note that this UUID is not the
                    same as the invitation one, as jid can be used publicly (leaking the
                    UUID), and invitation UUID give access to account.
                in case of conflict, a suffix number is added to the account until a free
                    one if found (with a failure if SUFFIX_MAX is reached)
            password(unicode, None): password to use (will be used for XMPP account and
                                     profile)
                None to automatically generate one
            name(unicode, None): name of the invitee
                will be set as profile identity if present
            host_name(unicode, None): name of the host
            email(unicode, None): email to send the invitation to
                if None, no invitation email is sent, you can still associate email using
                    extra
                if email is used, extra can't have "email" key
            language(unicode): language of the invitee (used notabily to translate the
                               invitation)
                TODO: not used yet
            url_template(unicode, None): template to use to construct the invitation URL
                use {uuid} as a placeholder for identifier
                use None if you don't want to include URL (or if it is already specified
                    in custom message)
                /!\ you must put full URL, don't forget https://
                /!\ the URL will give access to the invitee account, you should warn in
                    message to not publish it publicly
            message_subject(unicode, None): customised message body for the invitation
                                            email
                None to use default subject
                uses the same substitution as for message_body
            message_body(unicode, None): customised message body for the invitation email
                None to use default body
                use {name} as a place holder for invitee name
                use {url} as a placeholder for the invitation url
                use {uuid} as a placeholder for the identifier
                use {app_name} as a placeholder for this software name
                use {app_url} as a placeholder for this software official website
                use {profile} as a placeholder for host's profile
                use {host_name} as a placeholder for host's name
            extra(dict, None): extra data to associate with the invitee
                some keys are reserved:
                    - created (creation date)
                if email argument is used, "email" key can't be used
            profile(unicode, None): profile of the host (person who is inviting)
        @return (dict[unicode, unicode]): dictionary with:
            - UUID associated with the invitee (key: id)
            - filled extra dictionary, as saved in the databae
        """
        ## initial checks
        extra = kwargs.pop('extra', {})
        if set(kwargs).intersection(extra):
            raise ValueError(
                _("You can't use following key(s) in both args and extra: {}").format(
                ', '.join(set(kwargs).intersection(extra))))

        self.checkExtra(extra)

        email = kwargs.pop('email', None)

        existing = await self.getExistingInvitation(email)
        if existing is not None:
            log.info(f"There is already an invitation for {email!r}")
            extra.update(existing)
            del extra[KEY_ID]

        emails_extra = kwargs.pop('emails_extra', [])
        if not email and emails_extra:
            raise ValueError(
                _('You need to provide a main email address before using emails_extra'))

        if (email is not None
            and not 'url_template' in kwargs
            and not 'message_body' in kwargs):
            raise ValueError(
                _("You need to provide url_template if you use default message body"))

        ## uuid
        log.info(_("creating an invitation"))
        id_ = existing[KEY_ID] if existing else str(shortuuid.uuid())

        if existing is None:
            await self._createAccountAndProfile(id_, kwargs, extra)

        profile = kwargs.pop('profile', None)
        guest_profile = extra[KEY_GUEST_PROFILE]
        jid_ = jid.JID(extra[KEY_JID])

        ## identity
        name = kwargs.pop('name', None)
        password = extra[KEY_PASSWORD]
        if name is not None:
            extra['name'] = name
            try:
                id_plugin = self.host.plugins['IDENTITY']
            except KeyError:
                pass
            else:
                await self.host.connect(guest_profile, password)
                guest_client = self.host.getClient(guest_profile)
                await id_plugin.setIdentity(guest_client, {'nicknames': [name]})
                await self.host.disconnect(guest_profile)

        ## email
        language = kwargs.pop('language', None)
        if language is not None:
            extra['language'] = language.strip()

        if email is not None:
            extra['email'] = email
            data_format.iter2dict(KEY_EMAILS_EXTRA, extra)
            url_template = kwargs.pop('url_template', '')
            format_args = {
                'uuid': id_,
                'app_name': C.APP_NAME,
                'app_url': C.APP_URL}

            if name is None:
                format_args['name'] = email
            else:
                format_args['name'] = name

            if profile is None:
                format_args['profile'] = ''
            else:
                format_args['profile'] = extra['profile'] = profile

            host_name = kwargs.pop('host_name', None)
            if host_name is None:
                format_args['host_name'] = profile or _("somebody")
            else:
                format_args['host_name'] = extra['host_name'] = host_name

            invite_url = url_template.format(**format_args)
            format_args['url'] = invite_url

            await sat_email.sendEmail(
                self.host.memory.config,
                [email] + emails_extra,
                (kwargs.pop('message_subject', None) or DEFAULT_SUBJECT).format(
                    **format_args),
                (kwargs.pop('message_body', None) or DEFAULT_BODY).format(**format_args),
            )

        ## roster

        # we automatically add guest to host roster (if host is specified)
        # FIXME: a parameter to disable auto roster adding would be nice
        if profile is not None:
            try:
                client = self.host.getClient(profile)
            except Exception as e:
                log.error(f"Can't get host profile: {profile}: {e}")
            else:
                await self.host.updateContact(client, jid_, name, ['guests'])

        if kwargs:
            log.warning(_("Not all arguments have been consumed: {}").format(kwargs))

        ## extra data saving
        self.invitations[id_] = extra

        extra[KEY_ID] = id_

        return extra

    def _simpleCreate(self, invitee_email, invitee_name, url_template, extra_s, profile):
        client = self.host.getClient(profile)
        # FIXME: needed because python-dbus use a specific string class
        invitee_email = str(invitee_email)
        invitee_name = str(invitee_name)
        url_template = str(url_template)
        extra = data_format.deserialise(extra_s)
        d = defer.ensureDeferred(
            self.simpleCreate(client, invitee_email, invitee_name, url_template, extra)
        )
        d.addCallback(lambda data: {k: str(v) for k,v in data.items()})
        return d

    async def simpleCreate(
        self, client, invitee_email, invitee_name, url_template, extra):
        """Simplified method to invite somebody by email"""
        return await self.create(
            name=invitee_name,
            email=invitee_email,
            url_template=url_template,
            profile=client.profile,
        )

    def get(self, id_):
        """Retrieve invitation linked to uuid if it exists

        @param id_(unicode): UUID linked to an invitation
        @return (dict[unicode, unicode]): data associated to the invitation
        @raise KeyError: there is not invitation with this id_
        """
        return self.invitations[id_]

    def _delete(self, id_):
        return defer.ensureDeferred(self.delete(id_))

    async def delete(self, id_):
        """Delete an invitation data and associated XMPP account"""
        log.info(f"deleting invitation {id_}")
        data = await self.get(id_)
        guest_profile = data['guest_profile']
        password = data['password']
        try:
            await self.host.connect(guest_profile, password)
            guest_client = self.host.getClient(guest_profile)
            # XXX: be extra careful to use guest_client and not client below, as this will
            #   delete the associated XMPP account
            log.debug("deleting XMPP account")
            await self.host.plugins['XEP-0077'].unregister(guest_client, None)
        except (error.StanzaError, sasl.SASLAuthError) as e:
            log.warning(
                f"Can't delete {guest_profile}'s XMPP account, maybe it as already been "
                f"deleted: {e}")
        try:
            await self.host.memory.asyncDeleteProfile(guest_profile, True)
        except Exception as e:
            log.warning(f"Can't delete guest profile {guest_profile}: {e}")
        log.debug("removing guest data")
        await self.invitations.adel(id_)
        log.info(f"{id_} invitation has been deleted")

    def _modify(self, id_, new_extra, replace):
        return self.modify(id_, {str(k): str(v) for k,v in new_extra.items()},
                           replace)

    def modify(self, id_, new_extra, replace=False):
        """Modify invitation data

        @param id_(unicode): UUID linked to an invitation
        @param new_extra(dict[unicode, unicode]): data to update
            empty values will be deleted if replace is True
        @param replace(bool): if True replace the data
            else update them
        @raise KeyError: there is not invitation with this id_
        """
        self.checkExtra(new_extra)
        def gotCurrentData(current_data):
            if replace:
                new_data = new_extra
                for k in EXTRA_RESERVED:
                    try:
                        new_data[k] = current_data[k]
                    except KeyError:
                        continue
            else:
                new_data = current_data
                for k,v in new_extra.items():
                    if k in EXTRA_RESERVED:
                        log.warning(_("Skipping reserved key {key}").format(key=k))
                        continue
                    if v:
                        new_data[k] = v
                    else:
                        try:
                            del new_data[k]
                        except KeyError:
                            pass

            self.invitations[id_] = new_data

        d = self.invitations[id_]
        d.addCallback(gotCurrentData)
        return d

    def _list(self, profile=C.PROF_KEY_NONE):
        return defer.ensureDeferred(self.list(profile))

    async def list(self, profile=C.PROF_KEY_NONE):
        """List invitations

        @param profile(unicode): return invitation linked to this profile only
            C.PROF_KEY_NONE: don't filter invitations
        @return list(unicode): invitations uids
        """
        invitations = await self.invitations.all()
        if profile != C.PROF_KEY_NONE:
            invitations = {id_:data for id_, data in invitations.items()
                           if data.get('profile') == profile}

        return invitations
