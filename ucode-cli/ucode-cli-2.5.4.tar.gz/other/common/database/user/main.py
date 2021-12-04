import json

import redis

from other.common.file.io import remove_if_exists, write_file

import mysql.connector

_HOST = 'localhost'
_PORT = '3311'
_USER = 'ucode'
_PASSWORD = 'ucode1234'
_DATABASE = 'ucode_19_02'


def get_ucode_user_token():
    mydb = mysql.connector.connect(
        host=_HOST,
        port=_PORT,
        user=_USER,
        password=_PASSWORD,
        database=_DATABASE
    )
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute(
        '''
select user_id, token from user_token where id in (select max(id) from user_token where expired_at > now() and is_deleted = 0 group by user_id) limit 1000
        '''
    )
    users = mycursor.fetchall()
    tokens = [user['token'] for user in users]
    remove_if_exists('other/common/database/variable/ucode_student_user_token.py')
    write_file('other/common/database/variable/ucode_student_user_token.py',
               'UCODE_STUDENT_USER_TOKEN = ' + json.dumps(tokens, indent=2))
    mycursor.close()
    mydb.close()
    redisClient = redis.StrictRedis(host='localhost',
                                    port=6379,
                                    db=0)
    key = 'tokens'
    redisClient.lpush(key, *tokens)
    return tokens
