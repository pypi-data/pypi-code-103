import asyncio
import os
from autobahn.wamp.types import PublishOptions
from .crossbar import CrossbarConnection

class Reswarm():
    def __init__(self, serial_number=None):
        self.serial_number = os.environ.get(
            'DEVICE_SERIAL_NUMBER', serial_number)
        if self.serial_number == None:
            raise Exception("serial number is missing")

        self.cb_connection = CrossbarConnection(serial_number)
        self.cb_connection.start()

    def publish(self, topic: str, *args: list):
        device_name = os.environ.get("DEVICE_NAME")

        session = self.cb_connection.getSession()
        threadedLoop = self.cb_connection.getEventLoop()

        extra = {
            "DEVICE_SERIAL_NUMBER": self.serial_number,
            "options": PublishOptions(acknowledge=True)
        }

        if device_name:
            extra["DEVICE_NAME"] = device_name

        async def publishFunc():
            return await session.publish(topic, *args, **extra)

        concurrentFuture = asyncio.run_coroutine_threadsafe(publishFunc(), threadedLoop)
        return asyncio.wrap_future(concurrentFuture)