import requests

class Objects:
    base_url = 'https://objects.kimiko.io/v1'

    def __init__(self, account_id, api_key):
        self.account_id = account_id
        self.api_key = api_key
        self.url_auth = f'account_id={self.account_id}&api_key={self.api_key}'


    @classmethod
    def client(cls, account_id, api_key):
        return cls(account_id, api_key)
    

    def objects(self):
        r = requests.get(f'{Objects.base_url}?{self.url_auth}')
        if r.ok:
            return r.json().get('data')
        else:
            return []

    def create_object(self, object_key: str, name: str, fields: dict = None, unique_fields: list = None):
        data = {k:v for k,v in ({'object_key': object_key, 'name': name, 'fields': fields, 'unique_fields': unique_fields}).items()}
        r = requests.post(f'{Objects.base_url}?{self.url_auth}', data=data)
        return r.json()

    def update_object(self, object_key, **kwargs):
        r = requests.put(f'{Objects.base_url}/{object_key}?{self.url_auth}', data={k:v for k,v in kwargs.items()})
        return r.json()

    def delete_object(self, object_key):
        r = requests.delete(f'{Objects.base_url}/{object_key}?{self.url_auth}')
        return r.json()


    def records(self, object_key, limit=None):
        r = requests.get(f'{Objects.base_url}/{object_key}/records?{self.url_auth}')
        if r.ok:
            return r.json().get('data')
        else:
            print(r.json())
            return []

    def create_record(self, object_key, **kwargs):
        r = requests.post(f'{Objects.base_url}/{object_key}/records?{self.url_auth}', data={k:v for k,v in kwargs.items()})
        return r.json()


    def update_record(self, object_key, record_id, **kwargs):
        r = requests.put(f'{Objects.base_url}/{object_key}/records/{record_id}?{self.url_auth}', data={k:v for k,v in kwargs.items()})
        return r.json()

    def delete_record(self, object_key, record_id):
        r = requests.delete(f'{Objects.base_url}/{object_key}/records/{record_id}?{self.url_auth}')
        return r.json()