import requests, time
from random import choice
import sys


class get_helper:
    def __init__(self, app):
        self.app = app

    def run(self, url, cookie=None):
        headers = self.app.config['get']['headers']
        headers['user-agent'] = choice(self.app.ua_list)
        if self.app.config['proxy']['enable_proxy']:
            while True:
                with open(self.app.config['proxy']['path'], 'r', encoding='utf-8-sig', newline='') as f:
                    proxies = [proxy for proxy in f]
                proxy = choice(proxies)
                if proxy not in self.app.using_proxies:
                    self.app.using_proxies.append(proxy)
                    # print(app.using_proxies)
                    break
            if self.app.config['proxy']['proxy_autentification']:
                proxies = {'http': f"http://{self.app.config['proxy']['login']}:{self.app.config['proxy']['password']}@{proxy}"}
            else:
                proxies = {"http": f"http://{proxy}", "https": f"https://{proxy}"}
        else:
            proxies = None
            proxy = None
        r = None
        attempt = 1
        limit = 3
        while attempt < limit:
            try:
                r = requests.get(url=url, proxies=proxies, headers=headers, timeout=30, cookies=cookie)
                print("Status code:", r.status_code, "Proxy:", proxy)
                break
            except Exception as e:
                self.app.log_error.error(e, exc_info=True)
                print(f'{self.app.config["bot_name"]} не подключился, осталось попыток:', limit - attempt)
                attempt += 1
                time.sleep(10)
        if r is None:
            self.app.sms(f'{self.app.config["bot_name"]} не удалось установить соединение')
            print('работу завершаю')
            sys.exit()
        time.sleep(2)
        try:
            self.app.using_proxies.remove(proxy)
        except Exception as e:
            self.app.log_error.error(e, exc_info=True)
        return r
