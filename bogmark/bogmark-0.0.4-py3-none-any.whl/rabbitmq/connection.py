import enum
import sys

import aio_pika

from bogmark.logger import get_logger

logger = get_logger(__name__)

async_connections = {}


class ConnectionType(enum.Enum):
    PUBLISHER = "publisher"
    CONSUMER = "consumer"


class CustomRobustConnection(aio_pika.RobustConnection):
    def _on_connection_close(self, connection, closing, *args, **kwargs):  # noqa: U100
        if self.reconnecting:
            return

        self.connected.clear()
        self.connection = None

        super()._on_connection_close(connection, closing)

        if self._closed:
            return

        logger.error("Connection to %s closed", self)
        sys.exit()


async def get_rabbit_async_connection(connection_type: ConnectionType, host, port, login, password, virtual_host, ssl):
    conn = async_connections.get(connection_type)
    if conn is None:
        conn = await aio_pika.connect(
            host=host,
            port=port,
            login=login,
            password=password,
            virtualhost=virtual_host,
            timeout=10,
            ssl=ssl,
            connection_class=CustomRobustConnection,
        )
        async_connections[connection_type] = conn
    return conn
