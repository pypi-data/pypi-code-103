from simple_async_mq_server import server

if __name__ == '__main__':
  test = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'siasmq'
  }
  
  server.start(10000, db_config=test)