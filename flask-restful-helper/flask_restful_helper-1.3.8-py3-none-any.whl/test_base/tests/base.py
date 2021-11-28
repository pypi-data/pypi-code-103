import json
from flask_testing import TestCase
from main import create_app
from tests.functions.db.db_common import DbCommon
import os


class TestBase(TestCase):
    username = None
    password = None
    login_url = '/account/login'  # 請填寫登入api url

    def create_app(self):
        return create_app(os.getenv('config_type', 'dev'))

    def setUp(self):
        db_common = DbCommon()
        if self.app.config['TEST_INIT_DB_ON_TEST']:
            db_common.init_db_data(db_conn_host=self.app.config['DB_HOST'],
                                   db_conn_port=self.app.config['DB_PORT'],
                                   db_conn_user=self.app.config['DB_USERNAME'],
                                   db_conn_password=str(self.app.config['DB_PASSWORD']),
                                   db_conn_db=self.app.config['DB_DATABASE'])
        for role_info in self.app.config['TEST_ACCOUNT']:
            for role_name, login_info in role_info.items():
                if role_name == self.role:
                    self.username = login_info['USERNAME']
                    self.password = login_info['PASSWORD']
                    break
        self.login(self.username, self.password)

    def login(self, username, password):
        data = {
            'username': username,
            'password': password,
        }
        with self.app.test_client() as client:
            res = client.post(self.login_url, data=json.dumps(data),
                              headers={"Content-Type": "application/json"})
        self.access_token = res.json['access_token']
        self.headers = {'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.access_token}'}
