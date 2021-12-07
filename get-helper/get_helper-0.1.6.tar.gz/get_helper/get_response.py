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
        proxy = None
        if self.app.config['proxy']['enable_proxy']:
            while True:
                with open(self.app.config['proxy'], 'r', encoding='utf-8-sig', newline='') as f:
                    proxies_list = [proxy for proxy in f]
                proxy = choice(proxies_list)
                if proxy not in self.app.using_proxies:
                    self.app.using_proxies.append(proxy)
                    break
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
                if self.app.config['proxy']['enable_proxy']:
                    print("Status code:", status_code, "Proxy:", proxy)
                else:
                    print("Status code:", status_code, "no proxy")
                break
            except Exception as e:
                self.app.log_error.error(e, exc_info=True)
                print('not connected, there are only', limit - attempt, 'attempts')
                attempt += 1
                time.sleep(2)
        try:
            self.app.using_proxies.remove(proxy)
        except Exception as e:
            self.app.log_error.error(e, exc_info=True)
        return r, status_code
