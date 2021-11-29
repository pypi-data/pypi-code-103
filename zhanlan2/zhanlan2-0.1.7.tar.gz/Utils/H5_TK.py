#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/22 16:23
# @Author  : Adyan
# @File    : H5_TK.py


import asyncio
import time
from pyppeteer.launcher import launch
from faker import Faker
from pyppeteer import launcher

# launcher.DEFAULT_ARGS.remove("--enable-automation")

fake = Faker()


class GetTK:
    def __init__(self, mongo_conn):
        self.mongo_conn = mongo_conn

    async def get_content(self, url):
        browser = await launch(
            {
                'headless': True,
                "args": [
                    "--disable-infobars",
                ],
                "dumpio": True,
                "userDataDir": "",
            }
        )
        page = await browser.newPage()
        await page.setViewport({'width': 1200, 'height': 700})
        # await page.setUserAgent(
        #     'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36')
        # try:
        await page.goto(url, {'timeout': 0})
        # except:
        #     return url
        await page.evaluate(
            '''() =>{ Object.defineProperties(navigator, { webdriver:{ get: () => false } }) }''')
        await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
        await page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
        await page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')
        await asyncio.sleep(2)
        cookie_list = await page.cookies()
        print(cookie_list)
        cookies = {}
        for cookie in cookie_list:
            print(cookie.get("name"))
            if cookie.get("name") == '_m_h5_tk' or cookie.get("name") == '_m_h5_tk_enc':
                cookies[cookie.get("name")] = cookie.get("value")
                cookies['time'] = int(time.time() + 3600)
        self.mongo_conn.update_one({'id': '1'}, cookies)
        await browser.close()

    def headers(self):
        while True:
            user_agent = fake.chrome(
                version_from=63, version_to=80, build_from=999, build_to=3500
            )
            if "Android" in user_agent or "CriOS" in user_agent:
                continue
            else:
                break
        return user_agent

    def start(self):
        url = 'https://detail.1688.com/offer/627056024629.html?clickid=7ff082f5c2214f04a00580fcad6c8d52&sessionid=6947210c01f988d9ad53f73e6ec90f24'
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.get_content(url))
