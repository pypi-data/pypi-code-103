from asyncio import Queue
import socketio
from ..database.db import Database
from ..models.message import Message
from ..models.subscriber import Subscriber
from ..utilities.config import reporting_to_dashboard
from ..utilities.transformer import transform_to

# https://www.geeksforgeeks.org/python-list-comprehensions-vs-generator-expressions/


class MessageQueue:
    def __init__(self, socket, db_connection: Database) -> None:
        self.__subscribers: list[Subscriber] = []
        self.__queue = Queue()
        self.__socket: socketio.AsyncServer = socket
        self.__db_connection: Database = db_connection
        self.__is_reporting_to_dashboard: bool = reporting_to_dashboard()

    def __str__(self):
        return str(self.__queue)

    def __repr__(self):
        return str(self.__queue)

    @property
    def subscribers(self):
        return self.__subscribers

    @property
    def queue(self):
        return self.__queue

    @property
    def socket(self):
        return self.__socket

    @property
    def db_connection(self):
        return self.__db_connection

    @property
    def is_reporting_to_dashboard(self):
        return self.__is_reporting_to_dashboard

    @is_reporting_to_dashboard.setter
    def is_reporting_to_dashboard(self, is_reporting_to_dashboard):
        self.__is_reporting_to_dashboard = is_reporting_to_dashboard

    def find_subscriber_by_sid(self, sid: str):
        find_sub_generator = (
            sub for sub in self.subscribers if sub.sid == sid)
        return next(find_sub_generator, None)

    def add_subscriber(self, subscriber: Subscriber):
        self.subscribers.append(subscriber)

    def remove_subscriber(self, sid: str):
        subscriber = self.find_subscriber_by_sid(sid)
        if subscriber is not None:
            self.subscribers.remove(subscriber)

    async def add_message(self, msg: Message):
        await self.queue.put(msg)
        print("msg", msg)

        # Creates the log message and inserts it in the database
        log_msg = msg.get_log_message()
        self.db_connection.insert(log_msg)

        # push new message to frontend
        if self.is_reporting_to_dashboard:
            await self.socket.emit('msg-published', data=log_msg)

    # TODO: Implement a way to determine which subscriber to send to (load balancing)
    def determine_subscriber(self):
        no_of_subscribers = len(self.subscribers)

        if self.__sent_msgs_count < no_of_subscribers:
            self.__sent_msgs_count += 1
            return self.__sent_msgs_count

    async def push_messages(self):
        if len(self.subscribers) == 0:
            print('No subscribers online')
            return

        while not self.queue.empty():
            try:
                msg: Message = await self.queue.get()

                # TODO: Send to one of multiple subscribers
                output_format = self.subscribers[0].output_format

                msg.content = transform_to(msg.content, output_format)
                await self.socket.emit(event=msg.topic, data=msg.get_publish_message(), to=self.subscribers[0].sid)

                self.queue.task_done()

                msg.consumed_time = self.db_connection.update(msg.uuid)
                msg.is_consumed = True

                # push new message to frontend
                if self.is_reporting_to_dashboard:
                    await self.socket.emit('msg-consumed', data=msg.get_log_message())

            except Exception as e:
                msg = None
                print("Subscribe ERROR:", e)
