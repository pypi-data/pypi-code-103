from aiohttp import web
import socketio
from .models.message import Message
from .models.subscriber import Subscriber
from .models.message_queue_collection import MessageQueueCollection
from .database.db import Database
from .utilities.helpers import current_datetime
from .utilities import config
from .api.dashboard_api import create_dashboard_api

# https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56

sio = socketio.AsyncServer(cors_allowed_origins='http://localhost:3000')
app = web.Application()

sio.attach(app)

message_queues: MessageQueueCollection = None


@sio.event
async def connect(sid, environ):
    print('connect ', sid)


@sio.event
def disconnect(sid):
    print('disconnect ', sid)
    message_queues.remove_subscriber(sid)
    print('Queues after disconnect', message_queues)


@sio.on('subscribe')
async def handle_subscription(sid, data):
    # Add the session id to the data dict
    data['sid'] = sid

    # Creates a subscriber and adds them to a queue
    subscriber = Subscriber(**data)
    message_queues.add_subscriber(subscriber)
    print('Queues after new subcriber', message_queues)

    # Publish the topic for the subscriber
    await message_queues.publish_topic(subscriber.topic)


@sio.on('publish')
async def handle_published_msg(sid, data):
    print('message ', data)

    # Reject if input is of bytes type
    if isinstance(data['content'], bytes):
        return

    # Create the message
    msg = Message(
        topic=data['topic'],
        content_format=data['content_format'],
        content=data['content'],
        published_time=current_datetime())

    # Place the message in the queue for the topic
    await message_queues.add_message(msg)

    # after the log entry has been created the topic will be published
    await message_queues.publish_topic(msg.topic)

test = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'siasmq'
}


def start(port: int, db_config: dict, report_to_dashboard=False):
    config.save_to_config(db_config, report_to_dashboard)
    Database.create_table_if_not_exists(db_config)

    message_queues = MessageQueueCollection(socket=sio)
    message_queues.create_and_populate_queues()
    
    print("Initiated queues: ", message_queues.queues)
    
    web.run_app(app, port=port)


if __name__ == '__main__':
    db_config = config.db_config()
    start(port=10000, db_config=db_config, report_to_dashboard=True)
