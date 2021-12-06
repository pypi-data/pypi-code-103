import random
import ujson
import asyncio
import nats
import logging

from nats.aio.client import Client as NATS
from nats.js.client import JetStream

from typing import Callable, Dict, Optional, List
from pydantic import BaseModel


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
