# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import json
import uuid
import redis
import traceback
from suanpan.g import g
from suanpan.log import logger
from suanpan.base import Context


class LocalMQ:
    def __init__(self, **kwds):
        pass

    def xadd(self, *args):
        print(args)

    def xreadgroup(self, *args, **kwds):
        return None

    def xgroup_create(self, *args, **kwds):
        pass


class Stream:
    def __init__(self):
        if g.get("mqType") == "redis":
            self.client = redis.Redis(
                host=g.get("mqRedisHost"),
                port=6379,
                decode_responses=True,
                socket_keepalive=True,
                socket_connect_timeout=1,
            )
        else:
            self.client = LocalMQ()

    def generateRequestId(self):
        return uuid.uuid4().hex

    def generateMessage(self):
        message = Context(extra=json.dumps({}),
                          request_id=self.generateRequestId())
        return message

    def sendMessage(self, data, message):
        output = {
            "node_id": g.nodeId,
            "request_id": message.request_id,
            "extra": message.extra,
            "success": "true",
            **data
        }
        return self.client.xadd(g.get("streamSendQueue"),
                                output,
                                id="*",
                                maxlen=int(
                                    g.get("streamSendQueueMaxLength",
                                          default=2000)),
                                approximate=(not False if g.get(
                                    "streamSendQueueTrimImmediately",
                                    default="false") == "false" else True))

    def createQueue(self,
                    name,
                    group="default",
                    consumeID="0",
                    force=False,
                    existOk=False):
        logger.debug(f"Create Queue {name}-{group}")
        if force:
            self.deleteQueue(name)
        return self._createQueue(name,
                                 group=group,
                                 consumeID=consumeID,
                                 existOk=existOk)

    def _createQueue(self,
                     name,
                     group="default",
                     consumeID="0",
                     existOk=False):
        try:
            return self.client.xgroup_create(name,
                                             group,
                                             id=consumeID,
                                             mkstream=True)
        except redis.RedisError as e:
            tracebackInfo = traceback.format_exc()
            logger.debug(f"Redis create queue error: {tracebackInfo}")
            if not existOk:
                raise Exception(f"Redis queue {name} existed") from e
            return None

    def deleteQueue(self, *names):
        return self.client.delete(*names)

    def subscribeMessage(self):
        self.createQueue(g.get("streamRecvQueue"),
                         group=g.nodeGroup,
                         existOk=True)
        logger.debug("Subscribing Messages...")
        while True:
            try:
                messages = self.client.xreadgroup(
                    g.nodeGroup,
                    g.nodeId, {g.get("streamRecvQueue"): ">"},
                    count=1,
                    block=int(g.get("streamRecvQueueBlock", default=60000)),
                    noack=False)
            except Exception as e:  # pylint: disable=broad-except
                logger.info(f"Error in receiving messages. Wait 0s")
                self.createQueue(g.get("streamRecvQueue"),
                                 group=g.nodeGroup,
                                 existOk=True)
                continue

            if messages:
                for message in messages:
                    queue, items = message
                    for item in items:
                        mid, data = item
                        self.client.xack(queue, g.nodeGroup, mid)
                        requestId = data["id"]
                        extra = data["extra"]
                        context = Context(extra=extra,
                                          request_id=requestId,
                                          args=Context())
                        try:
                            for k, v in data.items():
                                if k.startswith("in") and k[-1].isdigit():
                                    context.update({k: v})
                            yield context
                        except Exception as e:
                            logger.info(
                                f"Receive wrong message from upstream: {str(e)}"
                            )
