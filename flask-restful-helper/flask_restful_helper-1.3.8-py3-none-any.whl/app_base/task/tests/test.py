import json


class User(object):
    users_url = ''

    def test_list_all_users_return_200_or_204(self):
        with self.app.test_client() as client:
            res = client.get(self.users_url,
                             headers=self.headers)
            if res.status_code != 200 and res.status_code != 204:
                raise Exception(f'回傳status_code:{res.status_code}')

    def test_create_user(self):
        with self.app.test_client() as client:
            data = {}
            res = client.post(self.users_url, data=json.dumps(data), headers=self.headers)
            self.assertStatus(res, 201)

    def test_update_user(self):
        with self.app.test_client() as client:
            data = {}
            res = client.post(self.users_url, data=json.dumps(data), headers=self.headers)
            self.assertStatus(res, 201)
            row_id = res.json['data']['id']
        with self.app.test_client() as client:
            data = {}
            res = client.patch(f'{self.users_url}/{row_id}',
                               data=json.dumps(data),
                               headers=self.headers)
            self.assertStatus(res, 200)
        with self.app.test_client() as client:
            res = client.get(f'{self.users_url}/{row_id}', headers=self.headers)
            self.assertStatus(res, 200)
            for key, value in data.items():
                if res.json['data'][key] != value:
                    raise Exception(f"{key}:{value}, actual value:{res.json['data'][key]}")

    def test_delete_user(self):
        with self.app.test_client() as client:
            data = {}
            res = client.post(self.users_url, data=json.dumps(data), headers=self.headers)
            self.assertStatus(res, 201)
            row_id = res.json['data']['id']
        with self.app.test_client() as client:
            res = client.delete(f'{self.users_url}/{row_id}',
                                headers=self.headers)
            self.assertStatus(res, 204)
        with self.app.test_client() as client:
            res = client.get(f'{self.users_url}/{row_id}',
                             headers=self.headers)
            self.assertStatus(res, 404)
