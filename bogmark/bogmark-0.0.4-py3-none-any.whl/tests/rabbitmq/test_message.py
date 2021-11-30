import pytest
from pytest_mock import MockerFixture

from monite.rabbitmq.connection import ConnectionType, get_rabbit_async_connection
from monite.rabbitmq.message import Message, NoQueueExistsError


@pytest.mark.asyncio
async def test_message_publish(mocker: MockerFixture, result_holder):
    pass
    # rabbit_conn = await get_rabbit_async_connection(
    #     connection_type=ConnectionType.PUBLISHER,
    #     host="localhost",
    #     port=5672,
    #     login="guest",
    #     password="guest",
    #     ssl=False,
    #     virtual_host="/",
    # )
    # async with rabbit_conn.channel() as channel:
    #     message = Message(payload={"status": "deleted"}, max_retries=2)
    #     await message.publish(channel=channel, queue_name="API_status_change")
    #     with pytest.raises(NoQueueExistsError):
    #         await message.publish(channel=channel, queue_name="API")
