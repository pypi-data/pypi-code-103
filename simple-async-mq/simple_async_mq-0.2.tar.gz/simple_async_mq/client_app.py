import asyncio
import socketio

sio = socketio.AsyncClient()

@sio.event
async def connect():
    print('connection established')


@sio.event
async def disconnect():
    print('disconnected from server')


def receive_msg(topic):
    """
    Decorator
    """
    def inner(func):
        @sio.on(topic)
        async def handle_request(data):
            # call 'func' to return the data
            func(data)

    # returning inner function
    return inner

async def publish_msg(topic: str ='topic1', content_format: str ='json', content: str='{"name": "susan"}'):
    msg = {
    'topic': topic, 
    'content_format': content_format, 
    'content': content 
    }
    await sio.emit('publish', msg)


def connect(host: str, port: str, topic: str = None, output_format: str = 'json', topics: list[(str, str)] = None):
    """
    Connect to the message bus with one or multiple topics
    :param host: The host of the bus - e.g.: localhost
    :param port: The port of the bus - e.g.: 5000
    :param topic: The topic to subscribe to. Use this if you only will register subscription for one topic
    :output_format: the output format for the one topic - default is JSON
    :param topics: Should contain tuple with the topic and the desired output_format for that topic
    """
    async def main():
        try:
            if (topic is None and topics is None or 
                topic is not None and topics is not None):
                raise ValueError

            await sio.connect(f'http://{host}:{port}')

            if topic:
                await send_subscribe_msg(topic, output_format)
            else:
                for _topic, _output_format in topics:
                    await send_subscribe_msg(_topic, _output_format)
                
            await sio.wait()
        except ValueError as ve:
            print(ve)
        except Exception as e:
            print(e)

    asyncio.run(main())
    

async def send_subscribe_msg(topic: str, output_format: str):
    msg = {
        'topic': topic,
        'output_format': output_format
    }

    await sio.emit('subscribe', msg)