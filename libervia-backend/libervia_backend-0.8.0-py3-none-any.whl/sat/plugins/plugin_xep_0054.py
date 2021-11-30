#!/usr/bin/env python3

# SAT plugin for managing xep-0054
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2014 Emmanuel Gil Peyrot (linkmauve@linkmauve.fr)

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

import io
from base64 import b64decode, b64encode
from hashlib import sha1
from pathlib import Path
from typing import Optional
from zope.interface import implementer
from twisted.internet import threads, defer
from twisted.words.protocols.jabber import jid, error
from twisted.words.xish import domish
from twisted.python.failure import Failure
from wokkel import disco, iwokkel
from sat.core import exceptions
from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core.log import getLogger
from sat.core.xmpp import SatXMPPEntity
from sat.memory import persistent
from sat.tools import image

log = getLogger(__name__)

try:
    from PIL import Image
except:
    raise exceptions.MissingModule(
        "Missing module pillow, please download/install it from https://python-pillow.github.io"
    )

from twisted.words.protocols.jabber.xmlstream import XMPPHandler

IMPORT_NAME = "XEP-0054"

PLUGIN_INFO = {
    C.PI_NAME: "XEP 0054 Plugin",
    C.PI_IMPORT_NAME: IMPORT_NAME,
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0054", "XEP-0153"],
    C.PI_DEPENDENCIES: ["IDENTITY"],
    C.PI_RECOMMENDATIONS: [],
    C.PI_MAIN: "XEP_0054",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of vcard-temp"""),
}

AVATAR_PATH = "avatars"
AVATAR_DIM = (128, 128)

IQ_GET = '/iq[@type="get"]'
NS_VCARD = "vcard-temp"
VCARD_REQUEST = IQ_GET + '/vCard[@xmlns="' + NS_VCARD + '"]'  # TODO: manage requests

PRESENCE = "/presence"
NS_VCARD_UPDATE = "vcard-temp:x:update"
VCARD_UPDATE = PRESENCE + '/x[@xmlns="' + NS_VCARD_UPDATE + '"]'

HASH_SHA1_EMPTY = "da39a3ee5e6b4b0d3255bfef95601890afd80709"


class XEP_0054(object):

    def __init__(self, host):
        log.info(_("Plugin XEP_0054 initialization"))
        self.host = host
        self._i = host.plugins['IDENTITY']
        self._i.register(IMPORT_NAME, 'avatar', self.getAvatar, self.setAvatar)
        self._i.register(IMPORT_NAME, 'nicknames', self.getNicknames, self.setNicknames)
        host.trigger.add("presence_available", self.presenceAvailableTrigger)

    def getHandler(self, client):
        return XEP_0054_handler(self)

    def presenceAvailableTrigger(self, presence_elt, client):
        try:
            avatar_hash = client._xep_0054_avatar_hashes[client.jid.userhost()]
        except KeyError:
            log.info(
                _("No avatar in cache for {profile}")
                .format(profile=client.profile))
            return True
        x_elt = domish.Element((NS_VCARD_UPDATE, "x"))
        x_elt.addElement("photo", content=avatar_hash)
        presence_elt.addChild(x_elt)
        return True

    async def profileConnecting(self, client):
        client._xep_0054_avatar_hashes = persistent.PersistentDict(
            NS_VCARD, client.profile)
        await client._xep_0054_avatar_hashes.load()

    def savePhoto(self, client, photo_elt, entity):
        """Parse a <PHOTO> photo_elt and save the picture"""
        # XXX: this method is launched in a separate thread
        try:
            mime_type = str(next(photo_elt.elements(NS_VCARD, "TYPE")))
        except StopIteration:
            mime_type = None
        else:
            if not mime_type:
                # MIME type not known, we'll try autodetection below
                mime_type = None
            elif mime_type == "image/x-png":
                # XXX: this old MIME type is still used by some clients
                mime_type = "image/png"

        try:
            buf = str(next(photo_elt.elements(NS_VCARD, "BINVAL")))
        except StopIteration:
            log.warning("BINVAL element not found")
            raise Failure(exceptions.NotFound())

        if not buf:
            log.warning("empty avatar for {jid}".format(jid=entity.full()))
            raise Failure(exceptions.NotFound())

        log.debug(_("Decoding binary"))
        decoded = b64decode(buf)
        del buf

        if mime_type is None:
            log.debug(
                f"no media type found specified for {entity}'s avatar, trying to "
                f"guess")

            try:
                mime_type = image.guess_type(io.BytesIO(decoded))
            except IOError as e:
                log.warning(f"Can't open avatar buffer: {e}")

            if mime_type is None:
                msg = f"Can't find media type for {entity}'s avatar"
                log.warning(msg)
                raise Failure(exceptions.DataError(msg))

        image_hash = sha1(decoded).hexdigest()
        with self.host.common_cache.cacheData(
            PLUGIN_INFO["import_name"],
            image_hash,
            mime_type,
        ) as f:
            f.write(decoded)
        return image_hash

    async def vCard2Dict(self, client, vcard_elt, entity_jid):
        """Convert a VCard_elt to a dict, and save binaries"""
        log.debug(("parsing vcard_elt"))
        vcard_dict = {}

        for elem in vcard_elt.elements():
            if elem.name == "FN":
                vcard_dict["fullname"] = str(elem)
            elif elem.name == "NICKNAME":
                nickname = vcard_dict["nickname"] = str(elem)
                await self._i.update(
                    client,
                    IMPORT_NAME,
                    "nicknames",
                    [nickname],
                    entity_jid
                )
            elif elem.name == "URL":
                vcard_dict["website"] = str(elem)
            elif elem.name == "EMAIL":
                vcard_dict["email"] = str(elem)
            elif elem.name == "BDAY":
                vcard_dict["birthday"] = str(elem)
            elif elem.name == "PHOTO":
                # TODO: handle EXTVAL
                try:
                    avatar_hash = await threads.deferToThread(
                        self.savePhoto, client, elem, entity_jid
                    )
                except (exceptions.DataError, exceptions.NotFound):
                    avatar_hash = ""
                    vcard_dict["avatar"] = avatar_hash
                except Exception as e:
                    log.error(f"avatar saving error: {e}")
                    avatar_hash = None
                else:
                    vcard_dict["avatar"] = avatar_hash
                if avatar_hash is not None:
                    await client._xep_0054_avatar_hashes.aset(
                        entity_jid.full(), avatar_hash)

                    if avatar_hash:
                        avatar_cache = self.host.common_cache.getMetadata(avatar_hash)
                        await self._i.update(
                            client,
                            IMPORT_NAME,
                            "avatar",
                            {
                                'path': avatar_cache['path'],
                                'filename': avatar_cache['filename'],
                                'media_type': avatar_cache['mime_type'],
                                'cache_uid': avatar_hash
                            },
                            entity_jid
                        )
                    else:
                        await self._i.update(
                            client, IMPORT_NAME, "avatar", None, entity_jid)
            else:
                log.debug("FIXME: [{}] VCard_elt tag is not managed yet".format(elem.name))

        return vcard_dict

    async def getVCardElement(self, client, entity_jid):
        """Retrieve domish.Element of a VCard

        @param entity_jid(jid.JID): entity from who we need the vCard
        @raise DataError: we got an invalid answer
        """
        iq_elt = client.IQ("get")
        iq_elt["from"] = client.jid.full()
        iq_elt["to"] = entity_jid.full()
        iq_elt.addElement("vCard", NS_VCARD)
        iq_ret_elt = await iq_elt.send(entity_jid.full())
        try:
            return next(iq_ret_elt.elements(NS_VCARD, "vCard"))
        except StopIteration:
            log.warning(_(
                "vCard element not found for {entity_jid}: {xml}"
                ).format(entity_jid=entity_jid, xml=iq_ret_elt.toXml()))
            raise exceptions.DataError(f"no vCard element found for {entity_jid}")

    async def updateVCardElt(self, client, entity_jid, to_replace):
        """Create a vcard element to replace some metadata

        @param to_replace(list[str]): list of vcard element names to remove
        """
        try:
            # we first check if a vcard already exists, to keep data
            vcard_elt = await self.getVCardElement(client, entity_jid)
        except error.StanzaError as e:
            if e.condition == "item-not-found":
                vcard_elt = domish.Element((NS_VCARD, "vCard"))
            else:
                raise e
        except exceptions.DataError:
            vcard_elt = domish.Element((NS_VCARD, "vCard"))
        else:
            # the vcard exists, we need to remove elements that we'll replace
            for elt_name in to_replace:
                try:
                    elt = next(vcard_elt.elements(NS_VCARD, elt_name))
                except StopIteration:
                    pass
                else:
                    vcard_elt.children.remove(elt)

        return vcard_elt

    async def getCard(self, client, entity_jid):
        """Ask server for VCard

        @param entity_jid(jid.JID): jid from which we want the VCard
        @result(dict): vCard data
        """
        entity_jid = self._i.getIdentityJid(client, entity_jid)
        log.debug(f"Asking for {entity_jid}'s VCard")
        try:
            vcard_elt = await self.getVCardElement(client, entity_jid)
        except exceptions.DataError:
            self._i.update(client, IMPORT_NAME, "avatar", None, entity_jid)
        except Exception as e:
            log.warning(_(
                "Can't get vCard for {entity_jid}: {e}"
                ).format(entity_jid=entity_jid, e=e))
        else:
            log.debug(_("VCard found"))
            return await self.vCard2Dict(client, vcard_elt, entity_jid)

    async def getAvatar(
            self,
            client: SatXMPPEntity,
            entity_jid: jid.JID
        ) -> Optional[dict]:
        """Get avatar data

        @param entity: entity to get avatar from
        @return: avatar metadata, or None if no avatar has been found
        """
        entity_jid = self._i.getIdentityJid(client, entity_jid)
        hashes_cache = client._xep_0054_avatar_hashes
        vcard = await self.getCard(client, entity_jid)
        if vcard is None:
            return None
        try:
            avatar_hash = hashes_cache[entity_jid.full()]
        except KeyError:
            if 'avatar' in vcard:
                raise exceptions.InternalError(
                    "No avatar hash while avatar is found in vcard")
            return None

        if not avatar_hash:
            return None

        avatar_cache = self.host.common_cache.getMetadata(avatar_hash)
        return self._i.avatarBuildMetadata(
                avatar_cache['path'], avatar_cache['mime_type'], avatar_hash)

    def _buildSetAvatar(self, client, vcard_elt, avatar_data):
        # XXX: this method is executed in a separate thread
        if avatar_data["media_type"] == "image/svg+xml":
            # for vector image, we save directly
            img_buf = open(avatar_data["path"], "rb")
        else:
            # for bitmap image, we check size and resize if necessary
            try:
                img = Image.open(avatar_data["path"])
            except IOError as e:
                raise exceptions.DataError(f"Can't open image: {e}")

            if img.size != AVATAR_DIM:
                img.thumbnail(AVATAR_DIM)
                if img.size[0] != img.size[1]:  # we need to crop first
                    left, upper = (0, 0)
                    right, lower = img.size
                    offset = abs(right - lower) / 2
                    if right == min(img.size):
                        upper += offset
                        lower -= offset
                    else:
                        left += offset
                        right -= offset
                    img = img.crop((left, upper, right, lower))
            img_buf = io.BytesIO()
            # PNG is well supported among clients, so we convert to this format
            img.save(img_buf, "PNG")
            img_buf.seek(0)
            avatar_data["media_type"] = "image/png"

        media_type = avatar_data["media_type"]
        photo_elt = vcard_elt.addElement("PHOTO")
        photo_elt.addElement("TYPE", content=media_type)
        image_b64 = b64encode(img_buf.read()).decode()
        img_buf.seek(0)
        photo_elt.addElement("BINVAL", content=image_b64)
        image_hash = sha1(img_buf.read()).hexdigest()
        img_buf.seek(0)
        with self.host.common_cache.cacheData(
            PLUGIN_INFO["import_name"], image_hash, media_type
        ) as f:
            f.write(img_buf.read())
            avatar_data['path'] = Path(f.name)
            avatar_data['filename'] = avatar_data['path'].name
        avatar_data['cache_uid'] = image_hash
        return image_hash

    async def setAvatar(self, client, avatar_data, entity):
        """Set avatar of the profile

        @param avatar_data(dict): data of the image to use as avatar, as built by
            IDENTITY plugin.
        @param entity(jid.JID): entity whose avatar must be changed
        """
        vcard_elt = await self.updateVCardElt(client, entity, ['PHOTO'])

        iq_elt = client.IQ()
        iq_elt.addChild(vcard_elt)
        await threads.deferToThread(
            self._buildSetAvatar, client, vcard_elt, avatar_data
        )
        # image is now at the right size/format

        await iq_elt.send()

        # FIXME: should send the current presence, not always "available" !
        await client.presence.available()

    async def getNicknames(self, client, entity):
        """get nick from cache, or check vCard

        @param entity(jid.JID): entity to get nick from
        @return(list[str]): nicknames found
        """
        vcard_data = await self.getCard(client, entity)
        try:
            return [vcard_data['nickname']]
        except (KeyError, TypeError):
            return []

    async def setNicknames(self, client, nicknames, entity):
        """Update our vCard and set a nickname

        @param nicknames(list[str]): new nicknames to use
            only first item of this list will be used here
        """
        nick = nicknames[0].strip()

        vcard_elt = await self.updateVCardElt(client, entity, ['NICKNAME'])

        if nick:
            vcard_elt.addElement((NS_VCARD, "NICKNAME"), content=nick)
        iq_elt = client.IQ()
        iq_elt.addChild(vcard_elt)
        await iq_elt.send()


@implementer(iwokkel.IDisco)
class XEP_0054_handler(XMPPHandler):

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host

    def connectionInitialized(self):
        self.xmlstream.addObserver(VCARD_UPDATE, self._update)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_VCARD)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

    async def update(self, presence):
        """Called on <presence/> stanza with vcard data

        Check for avatar information, and get VCard if needed
        @param presence(domish.Element): <presence/> stanza
        """
        client = self.parent
        entity_jid = self.plugin_parent._i.getIdentityJid(
            client, jid.JID(presence["from"]))

        try:
            x_elt = next(presence.elements(NS_VCARD_UPDATE, "x"))
        except StopIteration:
            return

        try:
            photo_elt = next(x_elt.elements(NS_VCARD_UPDATE, "photo"))
        except StopIteration:
            return

        given_hash = str(photo_elt).strip()
        if given_hash == HASH_SHA1_EMPTY:
            given_hash = ""

        hashes_cache = client._xep_0054_avatar_hashes

        old_hash = hashes_cache.get(entity_jid.full())

        if old_hash == given_hash:
            # no change, we can return…
            if given_hash:
                # …but we double check that avatar is in cache
                avatar_cache = self.host.common_cache.getMetadata(given_hash)
                if avatar_cache is None:
                    log.debug(
                        f"Avatar for [{entity_jid}] is known but not in cache, we get "
                        f"it"
                    )
                    # getCard will put the avatar in cache
                    await self.plugin_parent.getCard(client, entity_jid)
                else:
                    log.debug(f"avatar for {entity_jid} is already in cache")
            return

        if given_hash is None:
            # XXX: we use empty string to indicate that there is no avatar
            given_hash = ""

        await hashes_cache.aset(entity_jid.full(), given_hash)

        if not given_hash:
            await self.plugin_parent._i.update(
                client, IMPORT_NAME, "avatar", None, entity_jid)
            # the avatar has been removed, no need to go further
            return

        avatar_cache = self.host.common_cache.getMetadata(given_hash)
        if avatar_cache is not None:
            log.debug(
                f"New avatar found for [{entity_jid}], it's already in cache, we use it"
            )
            await self.plugin_parent._i.update(
                client,
                IMPORT_NAME, "avatar",
                {
                    'path': avatar_cache['path'],
                    'filename': avatar_cache['filename'],
                    'media_type': avatar_cache['mime_type'],
                    'cache_uid': given_hash,
                },
                entity_jid
            )
        else:
            log.debug(
                "New avatar found for [{entity_jid}], requesting vcard"
            )
            vcard = await self.plugin_parent.getCard(client, entity_jid)
            if vcard is None:
                log.warning(f"Unexpected empty vCard for {entity_jid}")
                return
            computed_hash = client._xep_0054_avatar_hashes[entity_jid.full()]
            if computed_hash != given_hash:
                log.warning(
                    "computed hash differs from given hash for {entity}:\n"
                    "computed: {computed}\ngiven: {given}".format(
                        entity=entity_jid, computed=computed_hash, given=given_hash
                    )
                )

    def _update(self, presence):
        defer.ensureDeferred(self.update(presence))
