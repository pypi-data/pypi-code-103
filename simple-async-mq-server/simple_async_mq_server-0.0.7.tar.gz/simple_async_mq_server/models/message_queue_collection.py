from ..database.db import Database
from ..models.message import Message
from ..utilities import helpers
from ..models.message_queue import MessageQueue
from ..models.subscriber import Subscriber
import socketio

class MessageQueueCollection:

    def __init__(self, socket) -> None:
        self.__queues: dict[str, MessageQueue] = dict()
        self.__socket: socketio.AsyncServer = socket
        self.__db_connection: Database = Database()

    def __str__(self):
        return str(self.queues)

    def __repr__(self):
        return str(self.queues)

    @property
    def queues(self):
        return self.__queues

    @property
    def socket(self):
        return self.__socket

    @property
    def db_connection(self):
        return self.__db_connection
        
    def create_and_populate_queues(self):
        messages = self.db_connection.get_all()

        for msg in messages:
            message = Message(
                uuid=msg['uuid'],
                topic=msg['topic'],
                content_format=msg['content_format'],
                content=msg['content'],
                published_time=msg['published_time'])

            print("MESSAGE:", message)

            self.create_queue_if_not_exists(message.topic)
            self.queues[message.topic].queue.put_nowait(message)

    def create_queue_if_not_exists(self, topic):
        do_queue_exist = self.queues.get(topic)

        if(not do_queue_exist):
            self.queues[topic] = MessageQueue(
                socket=self.socket, 
                db_connection=self.db_connection
                )

    def add_subscriber(self, subscriber: Subscriber):
        self.create_queue_if_not_exists(subscriber.topic)

        queue = self.queues.get(subscriber.topic)

        queue.add_subscriber(subscriber)

    # Removes the subscriber from the queue(s)
    def remove_subscriber(self, sid: str):
        for queue in self.queues.values():
            queue.remove_subscriber(sid)

    async def add_message(self, msg):
        # Create the queue for the topic if it doesn't exist
        self.create_queue_if_not_exists(msg.topic)
    
        await self.queues[msg.topic].add_message(msg)

    async def publish_topic(self, topic):
        queue = self.queues.get(topic)
        
        if queue is None: 
            print(f"No messages! Topic: '{topic}' is not created")
            return
        
        await queue.push_messages()

    
