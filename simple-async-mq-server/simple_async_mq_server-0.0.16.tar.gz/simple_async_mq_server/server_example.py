import server

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'siasmq'
}

server.start(10000, db_config)
