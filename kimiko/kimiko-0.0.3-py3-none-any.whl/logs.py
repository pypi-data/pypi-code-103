import requests
from urllib.parse import urlencode

class Logs:
    base_url = 'https://logs.kimiko.io/v1'

    def __init__(self, account_id, api_key):
        self.account_id = account_id
        self.api_key = api_key
        self.url_auth = f'account_id={self.account_id}&api_key={self.api_key}'


    @classmethod
    def client(cls, account_id, api_key):
        return cls(account_id, api_key)
    

    def logs(self, source=None, event_type=None, limit=None):
        y = urlencode({k:v for k,v in ({'source': source, 'event_type': event_type, 'limit': limit}).items() if v})
        url = f'https://logs.kimiko.io/v1?{self.url_auth}'
        url = f'{url}&{y}' if y else url
        r = requests.get(url)
        if r.ok:
            return r.json().get('data')
        else:
            print(r.json())
            return []