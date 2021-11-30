import os
import re
from abc import abstractmethod
from traceback import format_exc

from aio_pika import Connection, IncomingMessage, Queue

from bogmark.logger import get_logger

from .message import Message

# in ms
DEAD_MESSAGE_TTL = 86400000 * 7
RETRY_TIME = 10 * 1000


class Worker:
    DATA_SCHEMA = None

    def __init__(self, connection, prefetch: int = 1):
        if self.DATA_SCHEMA is None:
            raise AttributeError("DATA_SCHEMA should be overwritten")

        self.prefetch = prefetch

        self.logger = get_logger(__name__, type(self))

        self.connection: Connection = connection
        self.current_message: Message = None
        self._channel = None

    @staticmethod
    def _camel_to_snake(s):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()

    async def _declare_queues_and_exchanges(self, fanout_exchange_name):
        # main queue declaration
        await self._channel.set_qos(prefetch_count=self.prefetch)

        main_exchange = await self._channel.declare_exchange("amq.direct", durable=True)
        queue = await self._channel.declare_queue(
            name=self.queue(),
            durable=True,
            arguments={"x-dead-letter-exchange": "dlx", "x-dead-letter-routing-key": self.dq_queue},
        )
        await queue.bind(main_exchange, routing_key=self.queue())

        # dq queue. Here drop messages with retries
        dlx_exchange = await self._channel.declare_exchange("dlx", durable=True)
        await self._channel.declare_queue(
            name=self.dq_queue,
            durable=True,
            arguments={
                "x-message-ttl": RETRY_TIME,
                "x-dead-letter-exchange": "amq.direct",
                "x-dead-letter-routing-key": self.queue(),
            },
        )
        await queue.bind(dlx_exchange, routing_key=self.dq_queue)

        # xq queue. Here drop totally failed messages
        await self._channel.declare_queue(
            name=self.xq_queue, durable=True, arguments={"x-message-ttl": DEAD_MESSAGE_TTL}
        )

        if fanout_exchange_name:
            fanout_exchange = await self._channel.declare_exchange(
                fanout_exchange_name,
                durable=True,
                type="fanout",
            )
            queue = await self._channel.declare_queue(
                name=self.queue(),
                durable=True,
                arguments={"x-dead-letter-exchange": "dlx", "x-dead-letter-routing-key": self.dq_queue},
            )
            await queue.bind(fanout_exchange, routing_key="")

        return queue

    @classmethod
    def queue(cls):
        queue_prefix = os.environ["QUEUE_PREFIX"].upper()
        queue_name = cls._camel_to_snake(cls.__name__)
        return f"{queue_prefix}_{queue_name}"

    @property
    def xq_queue(self):
        """Que for storing dead messages for DEAD_MESSAGE_TTL"""
        return f"{self.queue()}.XQ"

    @property
    def dq_queue(self):
        """Que for requeue messages after RETRY_TIME"""
        return f"{self.queue()}.DQ"

    @abstractmethod
    async def on_message(self, message: Message):  # noqa: U100
        """Perform worker logic"""
        raise NotImplementedError

    async def consume(self, fanout_exchange_name=None):
        """Start consuming.
        If lost rabbit connection: put message in xq and stop consuming
        If exception occurred: put message in xq and continue consuming
        """

        channel = await self.connection.channel()
        self._channel = channel

        queue: Queue = await self._declare_queues_and_exchanges(fanout_exchange_name=fanout_exchange_name)
        self.logger.info(
            "Start consuming",
            extra={
                "worker": type(self).__name__,
                "queue": self.queue(),
            },
        )
        while True:
            try:
                async with queue.iterator() as queue_iter:
                    async for incoming_message in queue_iter:
                        incoming_message: IncomingMessage
                        self.logger.info(
                            ("start processing message %s" % incoming_message.message_id),
                            extra={
                                "worker": type(self).__name__,
                                "queue": self.queue(),
                            },
                        )
                        current_message: Message = await Message.from_incoming_message(
                            incoming_message=incoming_message, channel=channel, worker=self
                        )
                        if current_message is None:
                            incoming_message.ack()
                            continue

                        self.current_message = current_message

                        await self.on_message(current_message)

                        self.logger.info(
                            ("End processing message %s" % incoming_message.message_id),
                            extra={
                                "worker": type(self).__name__,
                                "queue": self.queue(),
                            },
                        )
                        incoming_message.ack()

            except Exception as e:
                error_traceback = format_exc()
                await self.current_message.drop(traceback=error_traceback)
                self.logger.exception(
                    e,
                    extra={
                        "worker": self.__class__.__name__,
                        "queue": self.queue(),
                    },
                )
                incoming_message.ack()
