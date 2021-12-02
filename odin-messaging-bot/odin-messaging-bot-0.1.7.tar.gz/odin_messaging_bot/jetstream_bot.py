import random
import ujson
import asyncio
import nats
import logging

from nats.aio.client import Client as NATS
from nats.js.client import JetStream

from typing import Callable, Dict, Optional, List
from pydantic import BaseModel


logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s:%(asctime)s:%(message)s")


class JetStreamMessagingBot(BaseModel):
    botname: str
    nats_url: str
    nc: Optional[NATS]
    js: Optional[JetStream]

    class Config:
        arbitrary_types_allowed = True

    async def connect(self):
        try:
            self.nc = await nats.connect(servers=[self.nats_url])
            logging.info(f"NATS: Connected")
            self.js = self.nc.jetstream()
            logging.info(f"NATS: JetStream {self.botname} Created")
        except TimeoutError as err:
            logging.debug(err)
            raise err

    async def add_stream(self, name: str, subjects: List[str]):
        logging.info(f"Adding Stream: {name} with subjects: {subjects}")
        await self.js.add_stream(name=name, subjects=subjects)

    async def publish(self, subject: str,  stream: str, payload: Dict):
        ack = await self.js.publish(subject=subject, payload=ujson.dumps(payload).encode(), stream=stream)
        logging.info(f'Publish Ack: stream={ack.stream}, sequence={ack.seq}')

    async def subscribe(self, subject: str, stream: str, cb: Optional[Callable] = None, durable: str = None, ordered_consumer: bool = True):
        await self.js.subscribe(subject=subject, stream=stream, cb=cb, durable=durable, ordered_consumer=ordered_consumer)
