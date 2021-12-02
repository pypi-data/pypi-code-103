import mysql.connector
from ..utilities.config import db_config
from datetime import datetime

class Database():
    def __init__(self):
        self.db_config = db_config()

    @classmethod
    def create_table_if_not_exists(self, db_settings):
        try:

            db = mysql.connector.connect(host=db_settings['host'], user=db_settings['user'], password=db_settings['password'])
            cursor = db.cursor()

            query = f"CREATE DATABASE IF NOT EXISTS {db_settings['database']}"
            cursor.execute(query)

            query = f"USE {db_settings['database']}"
            cursor.execute(query)

            query = """
                    CREATE TABLE IF NOT EXISTS queue_log(  
                        pk INT NOT NULL primary key AUTO_INCREMENT,
                        uuid VARCHAR(36) UNIQUE,
                        is_consumed TINYINT(1) NOT NULL,
                        topic VARCHAR(50) NOT NULL,
                        published_time DATETIME NOT NULL,
                        consumed_time DATETIME,
                        content_format VARCHAR(4) NOT NULL,
                        content VARCHAR(1000) NOT NULL
                    ) default charset utf8mb4;
                """
            cursor.execute(query)
                
        except mysql.connector.Error as error:
            print(f'Query failed:\n{error}')
        finally:
            if db.is_connected():
                cursor.close()
                db.close()

        

    def insert(self, msg) -> list:
      query = '''
        INSERT INTO queue_log (uuid, is_consumed, topic, published_time, content_format, content, consumed_time)
        VALUES(%s, %s, %s, %s, %s, %s, %s)
      '''

      query_params = list(msg.values())
      print("query_params", query_params)
      self.__query_db(query, query_params)

    def update(self, uuid):  # uuid
        query = '''
          UPDATE queue_log
          SET is_consumed = %s, consumed_time = %s
          WHERE uuid = %s
        '''

        query_params = [1,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        uuid]

        self.__query_db(query, query_params)
        print('q', query_params[1])
        return query_params[1]


    def get_all(self):
        query = "SELECT * FROM queue_log WHERE is_consumed = 0"

        result = self.__query_db(query, None, is_select_query=True)

        return result

    def __query_db(self, query: str, query_params, is_select_query=False):
        try:
            db = mysql.connector.connect(**self.db_config)

            if is_select_query:
                cursor = db.cursor(dictionary=True)
            else:
                cursor = db.cursor(prepared=True)

            cursor.execute(query, query_params)

            if(is_select_query):
                return cursor.fetchall()

            db.commit()
        except mysql.connector.Error as error:
            print(f'Query failed:\n{error}')
        finally:
            if db.is_connected():
                cursor.close()
                db.close()
