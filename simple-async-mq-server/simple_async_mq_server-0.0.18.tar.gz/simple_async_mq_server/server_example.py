 #import server

from simple_async_mq_server import server

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'siasmq'
}

server.start(10000, db_config)
