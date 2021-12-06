from random import choice
import requests
import time
from requests.adapters import HTTPAdapter


class get_helper:
    def __init__(self, app):
        self.app = app

    def run(self, url, cookie=None):
        headers = self.app.config['get']['headers']
        headers['user-agent'] = choice(self.app.ua_list)
        proxy = choice(self.app.proxy_list)
        if self.app.config['proxy']['enable_proxy']:
            if self.app.config['proxy']['proxy_autentification']:
                proxies = {'http': f"http://{self.app.config['proxy']['login']}:{self.app.config['proxy']['password']}@{proxy}"}
            else:
                proxies = {"http": f"http://{proxy}", "https": f"https://{proxy}"}
        else:
            proxies = None
        r = None
        status_code = 0
        attempt = 1
        limit = 3
        adapter = HTTPAdapter(max_retries=1)
        s = requests.Session()
        s.mount(self.app.config['host'], adapter)
        while attempt < limit:
            try:
                r = s.get(url=url, proxies=proxies, headers=headers, timeout=30, cookies=cookie)
                status_code = r.status_code
                print("Status code:", status_code)
                break
            except Exception as e:
                self.app.log_error.error(e, exc_info=True)
                print('not connected, there are only', limit - attempt, 'attempts')
                attempt += 1
                time.sleep(2)
        return r, status_code
