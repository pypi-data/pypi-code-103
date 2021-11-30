from traceback import format_exc
from uuid import UUID

import orjson
from aio_pika import Channel as AsyncChannel
from aio_pika import DeliveryMode, IncomingMessage
from aio_pika import Message as AsyncMessage
from aiormq.types import DeliveredMessage

from bogmark.logger import get_logger
from bogmark.structures.context import get_current_request_id, set_current_request_id

MAX_RETRIES = 5


class NoRequestIdExceptionError(Exception):
    pass


class NoQueueExistsError(Exception):
    pass


class Message:
    def __init__(
        self,
        payload: dict,
        max_retries: int = MAX_RETRIES,
    ):
        self.logger = get_logger(__name__, type(self))
        self.payload = payload

        self.properties = {
            "current_retries": 0,
            "max_retries": max_retries,
            "request_id": get_current_request_id(),
        }

        self._max_retries = max_retries
        self.is_failed = False
        self.traceback = None
        self._incoming_message: IncomingMessage = None
        self._channel: AsyncChannel = None
        self._id = None
        self._worker = None

    async def publish(self, channel: AsyncChannel, queue_name: str, content_type: str = "application/json"):
        """Publish message in queue but within async framework (thread save)

        :param AsyncChannel channel: Channel for rabbit connection
        :param str queue_name: routing key to publish in. Cause queue_name is always == routing_key on start
        :param str content_type: Content type of message body
        """
        r = await channel.default_exchange.publish(
            routing_key=queue_name,
            message=AsyncMessage(
                body=self.message_body, delivery_mode=DeliveryMode.PERSISTENT, content_type=content_type
            ),
        )
        if isinstance(r, DeliveredMessage):
            # should be Basic.Ack from pamqp.specifications
            self.logger.error(f"No route to {r.delivery.routing_key}. Sheeesh, did someone delete the queue?")
            raise NoQueueExistsError("Queue %s doesnt exists" % queue_name)
        return True

    async def broadcast(self, channel: AsyncChannel, fanout_exchange_name: str, content_type: str = "application/json"):
        """Publish message in exchange but within async framework (thread save)

        :param fanout_exchange_name: particulally this method is used for fanout exchanges
        :param AsyncChannel channel: Channel for rabbit connection
        :param str content_type: Content type of message body
        """

        exch = await channel.get_exchange(fanout_exchange_name)
        r = await exch.publish(
            routing_key="",
            message=AsyncMessage(
                body=self.message_body, delivery_mode=DeliveryMode.PERSISTENT, content_type=content_type
            ),
        )
        if isinstance(r, DeliveredMessage):
            # should be Basic.Ack from pamqp.specifications
            self.logger.error(f"No Queues binded to {fanout_exchange_name}. Sheeesh, did someone delete the queue?")
            raise NoQueueExistsError("No queues connected to exchange `%s`" % fanout_exchange_name)
        return True

    async def requeue(self):
        """Requeue message. Put it in dq and restarts every RETRY_TIME
        after self.max_retries put in xq

        """
        if self._worker is None:
            raise AttributeError("Cant requeue unprocessed message")

        dq_queue = self._worker.dq_queue
        if self.properties["current_retries"] >= self.properties["max_retries"]:
            self.logger.warning("Sending message %s into XQ" % self.message_id)
            await self.drop()
            return
        self.properties["current_retries"] += 1
        self.logger.info(
            "Retrying message: " + self.message_id, extra={"current_retries": self.properties["current_retries"]}
        )
        await self.publish(channel=self._channel, queue_name=dq_queue)

    async def drop(self, traceback: str = None):
        """Put message in xq where it will be stored for DEAD_MESSAGE_TTL

        :param str traceback: Traceback if exception occurred
        """
        self.is_failed = True
        self.traceback = traceback
        xq_queue = self._worker.xq_queue
        await self.publish(channel=self._channel, queue_name=xq_queue)

    @property
    def message_id(self) -> bool:
        """Is message failed (in xq)"""
        return self._id

    @property
    def request_id(self) -> [str, None]:
        """Current request id"""
        return self.properties["request_id"]

    @staticmethod
    def convertors(obj):
        if isinstance(obj, UUID):
            return str(obj)
        raise TypeError

    @property
    def message_body(self) -> bytes:
        """Dumps message payload and properties into bytes"""
        body_dict = {"payload": self.payload, "properties": self.properties}
        if self.is_failed:
            body_dict["traceback"] = self.traceback
        return orjson.dumps(body_dict, default=self.convertors)

    @classmethod
    async def from_incoming_message(cls, channel: AsyncChannel, incoming_message: IncomingMessage, worker):
        raw_payload = orjson.loads(incoming_message.body)
        msg_cls = Message(raw_payload)
        try:
            payload = raw_payload["payload"]
            properties = raw_payload["properties"]

            msg_cls.payload = payload
            msg_cls.properties = properties
        except KeyError as e:
            msg_cls.logger.exception(e)
            msg_cls.is_failed = True
            msg_cls.traceback = format_exc()
        finally:
            msg_cls._channel = channel
            msg_cls._id = incoming_message.message_id
            msg_cls._worker = worker
            set_current_request_id(msg_cls.request_id)
        if msg_cls.is_failed:
            await msg_cls.drop(msg_cls.traceback)
            return
        return msg_cls
