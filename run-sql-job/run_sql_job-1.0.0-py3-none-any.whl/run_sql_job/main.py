import os
import psycopg2 as psycopg2
import logging

DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_DATABASE = os.environ.get('DB_DATABASE')
SQL_PATH = os.environ.get('SQL_PATH')

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def run():
    connection = psycopg2.connect(user=DB_USER,
                                  password=DB_PASSWORD,
                                  host=DB_HOST,
                                  port=DB_PORT,
                                  database=DB_DATABASE)

    file = open(SQL_PATH,"r")
    sql_content = file.read()
    log.info('Sql content is : %s', sql_content)
    cursor = connection.cursor()
    cursor.execute(sql_content)
    connection.commit()
    log.info(f'Database is updated.')