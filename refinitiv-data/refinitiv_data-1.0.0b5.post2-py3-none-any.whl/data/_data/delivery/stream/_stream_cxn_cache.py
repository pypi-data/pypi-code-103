import asyncio
from typing import TYPE_CHECKING, Dict, List

from ._protocol_type import ProtocolType
from .event import StreamCxnEvent
from .null_stream_connection import NullStreamConnection
from ...content._content_type import ContentType

if TYPE_CHECKING:
    from ..stream import StreamConnection
    from ...core.session import Session

StreamConnections = List["StreamConnection"]


def on_event_listener(cxn: "StreamConnection", message: dict = None) -> None:
    on_event_callback = cxn.session.get_on_event_callback()

    if on_event_callback:
        on_event_callback(message)


def on_state_listener(cxn: "StreamConnection", message: dict = None) -> None:
    on_state_callback = cxn.session.get_on_state_callback()

    if on_state_callback:
        on_state_callback(message)


def add_listeners(cxn: "StreamConnection") -> None:
    # cxn.on(Event.UPDATE, on_state_listener)
    cxn.on(StreamCxnEvent.CONNECTING, on_event_listener)
    cxn.on(StreamCxnEvent.CONNECTED, on_event_listener)
    cxn.on(StreamCxnEvent.DISCONNECTED, on_event_listener)


def remove_listeners(cxn: "StreamConnection") -> None:
    # cxn.on(Event.UPDATE, on_state_listener)
    cxn.remove_listener(StreamCxnEvent.CONNECTING, on_event_listener)
    cxn.remove_listener(StreamCxnEvent.CONNECTED, on_event_listener)
    cxn.remove_listener(StreamCxnEvent.DISCONNECTED, on_event_listener)


class CacheItem:
    def __init__(
        self, cxn: "StreamConnection", content_type: ContentType, owner: dict
    ) -> None:
        self.content_type = content_type
        self.owner = owner
        self.cxn = cxn
        self.number_in_use = 0

        add_listeners(self.cxn)

    @property
    def is_using(self):
        return self.number_in_use > 0

    def inc_use(self):
        self.number_in_use += 1

    def dec_use(self):
        if self.number_in_use == 0:
            raise ValueError("CacheItem: number_in_use cannot be less 0")

        self.number_in_use -= 1

        if self.number_in_use == 0 and self.cxn.is_disconnecting:
            self.dispose()

    def dispose(self):
        self.number_in_use = -1
        self.owner.pop(self.content_type)
        self.content_type = ContentType.NONE
        self.owner = None

        remove_listeners(self.cxn)
        cxn = self.cxn
        cxn.dispose()
        cxn.join()
        self.cxn = None

    def __str__(self) -> str:
        if self.cxn:
            name = self.cxn.name
        else:
            name = "disposed"
        return f"CacheItem(cxn={name}, number_in_use={self.number_in_use})"


class StreamCxnCache(object):
    def __init__(self) -> None:
        self._cache: Dict["Session", Dict[ContentType, CacheItem]] = {}
        self._lock = asyncio.Lock()

    def has_cxn(self, session: "Session", content_type: ContentType) -> bool:
        item = self._cache.get(session, {}).get(content_type)
        return bool(item)

    def get_cxn(
        self,
        session: "Session",
        content_type: ContentType,
        protocol_type: ProtocolType,
    ) -> "StreamConnection":
        cxn = session.run_until_complete(
            self.get_cxn_async(session, content_type, protocol_type)
        )
        return cxn

    async def get_cxn_async(
        self,
        session: "Session",
        content_type: ContentType,
        protocol_type: ProtocolType,
    ) -> "StreamConnection":

        async with self._lock:

            if self.has_cxn(session, content_type):
                item = self._get_cache_item(session, content_type)
                cxn = item.cxn
                session.debug(
                    f"StreamCxnCache get from cache "
                    f"(id={cxn.id}, content_type={content_type}, "
                    f"protocol_type={protocol_type})"
                )
            else:
                from ...delivery.stream._stream_factory import create_stream_cxn

                cxn = create_stream_cxn(content_type, protocol_type, session)
                cxn.daemon = True
                cxn.start()

                item = self._add_cxn(cxn, session, content_type)

                session.debug(
                    f" + StreamCxnCache created new connection "
                    f"(id={cxn.id}, content_type={content_type}, "
                    f"protocol_type={protocol_type})"
                )

            session.debug(
                f"StreamCxnCache wait for connection "
                f"(id={cxn.id}, content_type={content_type}, "
                f"protocol_type={protocol_type})"
            )
            await cxn.prepared

            if cxn.is_disposed:
                raise AssertionError(f"Cannot prepare connection {cxn}")

            elif cxn.prepared.result() is True:
                item.inc_use()
                session.debug(f" <=== StreamCxnCache connection id={cxn.id} is ready")

            elif cxn.prepared.result() is False:
                session.error(
                    f"StreamCxnCache cannot get cxn"
                    f"(id={cxn.id}, content_type={content_type}, "
                    f"protocol_type={protocol_type})"
                    f", because it is disposed."
                )
                if self.has_cxn(session, content_type):
                    self.del_cxn(cxn, session, content_type)

                cxn.join()
                cxn = NullStreamConnection()

            else:
                raise AssertionError(f"Don't know what to do")

            return cxn

    def release(self, session: "Session", content_type: ContentType) -> None:
        if not self.has_cxn(session, content_type):
            raise ValueError(
                f"Cannot release stream connection, "
                f"because it’s not in the cache "
                f"(content_type={content_type}, session={session})"
            )

        item_by_content_type = self._cache[session]
        item = item_by_content_type[content_type]
        item.dec_use()
        session.debug(
            f" ===> StreamCxnCache release (item={item},\n"
            f"\t\tcontent_type={content_type},\n"
            f"\t\tsession={session})"
        )

    def del_cxn(
        self, cxn: "StreamConnection", session: "Session", content_type: ContentType
    ) -> None:
        if not cxn:
            raise ValueError(
                f"Cannot delete stream connection, "
                f"because it is empty (content_type={content_type}, "
                f"cxn={cxn}, session={session})"
            )

        if not self.has_cxn(session, content_type):
            raise ValueError(
                f"Cannot delete stream connection, "
                f"because already deleted (content_type={content_type}, "
                f"cxn={cxn}, session={session})"
            )

        item_by_content_type = self._cache[session]
        item = item_by_content_type[content_type]
        if item.is_using:
            raise AssertionError(
                f"Cannot delete stream connection, "
                f"because it is using (content_type={content_type}, "
                f"cxn={cxn}, session={session})"
            )

        cached_cxn = item.cxn

        if cxn is not cached_cxn:
            raise ValueError(
                f"Cannot delete stream connection, "
                f"because cxn is not the same \n"
                f"(cxn={cxn} != cached_cxn={cached_cxn},"
                f"content_type={content_type}, session={session})"
            )

        item.dispose()

    def has_cxns(self, session: "Session") -> bool:
        item_by_content_type = self._cache.get(session, {})
        has_cxns = bool(item_by_content_type.values())
        return has_cxns

    def get_cxns(self, session: "Session") -> StreamConnections:
        item_by_content_type = self._cache.get(session, {})
        return [item.cxn for item in item_by_content_type.values()]

    def close_cxns(self, session: "Session") -> None:
        session.run_until_complete(self.close_cxns_async(session))

    async def close_cxns_async(self, session: "Session") -> None:
        async def task(item):
            if item.is_using:
                await item.cxn.disconnect_async()

            else:
                await item.cxn.dispose_async()
                item.dispose()

        tasks = (task(item) for item in self._get_cache_items(session))
        await asyncio.gather(*tasks)
        self._cache.pop(session, None)

    def _add_cxn(
        self, cxn: "StreamConnection", session: "Session", content_type: ContentType
    ) -> CacheItem:
        if not cxn:
            raise ValueError(
                f"Cannot add stream connection, "
                f"because it is empty: content_type={content_type}, "
                f"cxn={cxn}, session={session}"
            )

        if self.has_cxn(session, content_type):
            raise ValueError(
                f"Cannot add stream connection, "
                f"because already added: content_type={content_type}, "
                f"cxn={cxn}, session={session}"
            )

        owner = self._cache.setdefault(session, {})
        item = CacheItem(cxn, content_type, owner)
        owner[content_type] = item
        return item

    def _get_cache_items(self, session: "Session") -> List[CacheItem]:
        item_by_content_type = self._cache.get(session, {})
        return [item for item in item_by_content_type.values()]

    def _get_cache_item(
        self, session: "Session", content_type: ContentType
    ) -> CacheItem:
        cache_item = self._cache[session][content_type]
        return cache_item

    def is_cxn_alive(self, session: "Session", content_type: ContentType) -> bool:
        is_alive = False
        if self.has_cxn(session, content_type):
            item = self._get_cache_item(session, content_type)
            is_alive = item.cxn.is_alive()

        return is_alive


stream_cxn_cache: StreamCxnCache = StreamCxnCache()
