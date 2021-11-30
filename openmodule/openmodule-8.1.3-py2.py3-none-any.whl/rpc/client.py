import logging
import threading
import time
from typing import Dict, Optional
from uuid import uuid4

from openmodule.models.rpc import RPCResponse, RPCRequest, RPCResult

from openmodule.core import OpenModuleCore
from openmodule.rpc.common import channel_to_response_topic, channel_to_request_topic


class RPCClient:
    class RPCEntry:
        def __init__(self, timeout):
            self.timestamp = time.time()
            self.timeout = timeout
            self.result = None
            self.ready = threading.Event()

    def __init__(self, core: OpenModuleCore, channels=None, timeout=3., cleanup_time=300):
        if channels is None:
            channels = []
        self.core = core
        self.log = logging.getLogger("rcp-client")
        self.lock = threading.Lock()
        self.results = dict()
        self.sync_timeout = timeout
        self.cleanup_time = cleanup_time
        self.running = True

        self.channels = []
        for channel in channels:
            self.register_channel(channel)

    def register_channel(self, channel):
        if not self.running:
            raise AssertionError("Cannot register channels when rpc client is shutdown")
        if channel not in self.channels:
            self.channels.append(channel)
            topic = channel_to_response_topic(channel)
            self.log.debug("Registering channel: {}".format(topic))
            self.core.messages.register_handler(topic, RPCResponse, self.receive)

    def unregister_channel(self, channel):
        self.channels.remove(channel)
        topic = channel_to_response_topic(channel)
        self.log.debug("Unregistering channel: {}".format(topic))
        self.core.sub_socket.unsubscribe(topic)

    def cleanup_old_results(self):
        now = time.time()
        with self.lock:
            to_delete = []
            for rpc_id, entry in self.results.items():
                if now > entry.timestamp + self.cleanup_time + entry.timeout:
                    to_delete.append(rpc_id)
            for rpc_id in to_delete:
                try:
                    del self.results[rpc_id]
                except KeyError:
                    pass

    def _call(self, channel: bytes, typ: str, request: Dict, timeout: float):
        rpc_id = str(uuid4())

        request = RPCRequest(rpc_id=rpc_id, resource=self.core.config.RESOURCE, name=self.core.config.NAME,
                             request=request, type=typ)
        topic = channel_to_request_topic(channel)
        self.results[rpc_id] = self.RPCEntry(timeout=timeout)
        self.core.publish(topic=topic, message=request)
        return rpc_id

    def check_result(self, rpc_id) -> Optional[RPCResult]:
        with self.lock:
            entry = self.results.get(str(rpc_id))
            if entry and entry.result:
                self.results.pop(rpc_id, None)
                status = "ok"
                if isinstance(entry.result, dict) and entry.result.get("status"):
                    status = entry.result["status"]
                return RPCResult(status=status, response=entry.result, rpc_id=rpc_id)

    def rpc(self, channel: bytes, type: str, request: Dict, timeout: float = None, blocking=True) -> RPCResult:
        self.cleanup_old_results()

        if timeout is None:
            timeout = self.sync_timeout

        if channel not in self.channels:
            self.register_channel(channel)

        rpc_id = self._call(channel, type, request, timeout)

        if blocking:
            self.log.debug("blocking rpc, this may cause delay")
            if self.results[rpc_id].ready.wait(timeout):
                return self.check_result(rpc_id)
            else:
                raise TimeoutError
        else:
            self.log.debug("non blocking rpc sent")
            return RPCResult(status="ok", response=None, rpc_id=rpc_id)

    def shutdown(self):
        self.running = False
        for channel in self.channels:
            self.unregister_channel(channel)

    def receive(self, response: RPCResponse):
        """handler that receives, saves and cleans up rpc responses"""

        with self.lock:
            if str(response.rpc_id) in self.results:
                self.results[str(response.rpc_id)].result = response.response
                self.results[str(response.rpc_id)].ready.set()
        self.cleanup_old_results()
