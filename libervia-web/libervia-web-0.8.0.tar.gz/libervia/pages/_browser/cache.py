from browser import window
from browser.local_storage import storage
from javascript import JSON
from dialog import notification
from bridge import Bridge

session_uuid = window.session_uuid
bridge = Bridge()

# XXX: we don't use browser.object_storage because it is affected by
#   https://github.com/brython-dev/brython/issues/1467 and mixing local_storage.storage
#   and object_storage was resulting in weird behaviour (keys found in one not in the
#   other)


class Cache:

    def __init__(self):
        try:
            cache = storage['libervia_cache']
        except KeyError:
            self.request_data_from_backend()
        else:
            cache = JSON.parse(cache)
            if cache['metadata']['session_uuid'] != session_uuid:
                print("data in cache are not valid for this session, resetting")
                del storage['libervia_cache']
                self.request_data_from_backend()
            else:
                self._cache = cache
                print("storage cache is used")

    @property
    def roster(self):
        return self._cache['roster']

    @property
    def identities(self):
        return self._cache['identities']

    def update(self):
        # FIXME: we use window.JSON as a workaround to
        #   https://github.com/brython-dev/brython/issues/1467
        print(f"updating: {self._cache}")
        storage['libervia_cache'] = window.JSON.stringify(self._cache)
        print("cache stored")

    def _store_if_complete(self):
        self._completed_count -= 1
        if self._completed_count == 0:
            del self._completed_count
            self.update()

    def getContactsCb(self, contacts):
        print("roster received")
        roster = self._cache['roster']
        for contact_jid, attributes, groups in contacts:
            roster[contact_jid] = {
                'attributes': attributes,
                'groups': groups,
            }
        self._store_if_complete()

    def identitiesBaseGetCb(self, identities_raw):
        print("base identities received")
        identities = JSON.parse(identities_raw)
        self._cache['identities'].update(identities)
        self._store_if_complete()

    def request_failed(self, exc, message):
        notification.show(message.format(exc=exc), "error")
        self._store_if_complete()

    def request_data_from_backend(self):
        self._cache = {
            'metadata': {
                "session_uuid": session_uuid,
            },
            'roster': {},
            'identities': {},
        }
        self._completed_count = 2
        print("requesting roster to backend")
        bridge.getContacts(
            callback=self.getContactsCb,
            errback=lambda e: self.request_failed(e, "Can't get contacts: {exc}")
        )
        print("requesting base identities to backend")
        bridge.identitiesBaseGet(
            callback=self.identitiesBaseGetCb,
            errback=lambda e: self.request_failed(e, "Can't get base identities: {exc}")
        )

    def _fill_identities_cb(self, new_identities_raw, callback):
        new_identities = JSON.parse(new_identities_raw)
        print(f"new identities: {new_identities.keys()}")
        self._cache['identities'].update(new_identities)
        self.update()
        if callback:
            callback()

    def fill_identities(self, entities, callback=None):
        """Check that identities for entities exist, request them otherwise"""
        to_get = {e for e in entities if e not in self._cache['identities']}
        if to_get:
            bridge.identitiesGet(
                list(to_get),
                ['avatar', 'nicknames'],
                callback=lambda identities: self._fill_identities_cb(
                    identities, callback),
                errback=lambda failure_: notification.show(
                    f"Can't get identities: {failure_}",
                    "error"
                )
            )
        else:
            # we already have all identities
            print("no missing identity")
            if callback:
                callback()

    def match_identity(self, entity_jid, text, identity=None):
        """Returns True if a text match an entity identity

        identity will be matching if its jid or any of its name contain text
        @param entity_jid: jid of the entity to check
        @param text: text to use for filtering. Must be in lowercase and stripped
        @param identity: identity data
            if None, it will be retrieved if jid is not matching
        @return: True if entity is matching
        """
        if text in entity_jid:
            return True
        if identity is None:
            try:
                identity = self.identities[entity_jid]
            except KeyError:
                print(f"missing identity: {entity_jid}")
                return False
        return any(text in n.lower() for n in identity['nicknames'])

    def matching_identities(self, text):
        """Return identities corresponding to a text

        """
        text = text.lower().strip()
        for entity_jid, identity in self._cache['identities'].items():
            if ((text in entity_jid
                 or any(text in n.lower() for n in identity['nicknames'])
                 )):
                yield entity_jid


cache = Cache()
roster = cache.roster
identities = cache.identities
