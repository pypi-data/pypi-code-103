#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/6 10:34
# @Author  : Adyan
# @File    : cookies.py


import asyncio
import json
import random
from pyppeteer import launcher
# launcher.DEFAULT_ARGS.remove("--enable-automation")
from pyppeteer.launcher import launch
from retrying import retry


class Cookies:
    async def slide(self, page):
        slider = await page.Jeval('#nc_1_n1z', 'node => node.style')
        if slider:
            print('当前页面出现滑块')
            flag, page = await self.mouse_slide(page=page)
            if flag:
                await page.keyboard.press('Enter')
                print("print enter", flag)
        else:
            print("正常进入")
            await page.keyboard.press('Enter')
            await asyncio.sleep(2)

            try:
                global error
                print("error_1:", error)
                error = await page.Jeval('.error', 'node => node.textContent')
                print("error_2:", error)
            except Exception as e:
                error = None
            finally:
                if error:
                    print('确保账户安全重新入输入')
                else:
                    print(page.url)
                    await asyncio.sleep(5)
                    return 'cg'

    async def get_content(self, us, url):
        # browser = await launch(options={'args': ['--no-sandbox']})
        browser = await launch({
            'headless': False,
            'handleSIGINT': False,
            'handleSIGTERM': False,
            'handleSIGHUP': False,
        })
        page = await browser.newPage()
        await page.setViewport({'width': 1200, 'height': 700})
        await page.setUserAgent(
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36')
        await page.goto(url)
        await asyncio.sleep(2)
        await page.evaluate(
            '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
        await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
        await page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
        await page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')

        if 'login' in page.url:
            print(us.get('name'), us.get('pwd'))
            await page.type("#fm-login-id", us.get('name'), {'delay': self.input_time_random() - 50})
            await page.type("#fm-login-password", us.get('pwd'), {'delay': self.input_time_random()})
            await self.slide(page)
        await asyncio.sleep(2)
        # if await self.slide(page) == 'cg':
        print('开始保存')
        cookie_list = await page.cookies()
        cookies = ""
        dels = {
            "tfstk": None,
            "isg": None,
            "l": None,
        }
        for cookie in cookie_list:
            if cookie.get("name") not in ["l", "tfstk", "isg"]:
                coo = "{}={}; ".format(cookie.get("name"), cookie.get("value"))
                cookies += coo
        print(cookies)
        await asyncio.sleep(1)
        await browser.close()
        return cookies[:-2]

    def retry_if_result_none(self, result):
        return result is None

    @retry(retry_on_result=retry_if_result_none, )
    async def mouse_slide(self, page=None):
        await asyncio.sleep(2)
        try:
            await page.hover('#nc_1_n1z')
            await page.mouse.down()
            await page.mouse.move(2000, 0, {'delay': random.randint(1000, 2000)})
            await page.mouse.up()
        except Exception as e:
            print(e, ':验证失败')
            return None, page
        else:
            await asyncio.sleep(2)
            slider_again = await page.Jeval('.nc-lang-cnt', 'node => node.textContent')
            if slider_again != '验证通过':
                return None, page
            else:
                print('验证通过')
                return 1, page

    def input_time_random(self):
        return random.randint(100, 151)

    def taobao_cookies(self, us):
        # us = random.choice([
        #     # {'name': '13316083124', 'pwd': 'Xyxeh1612'},
        #     {'name': '13302269234', 'pwd': 'XYing888'},
        #     # {'name': '13288460222', 'pwd': 'xiaoying888'},
        # ])
        # # print(us)
        # # url = 'https://sf.taobao.com/item_list.htm?spm=a213w.3064813.a214dqe.3.19375dadUJ0T8F&category=50025969'
        url = 'https://login.taobao.com/member/login.jhtml?'
        loop1 = asyncio.new_event_loop()
        asyncio.set_event_loop(loop1)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.get_content(us, url))

# if __name__ == '__main__':
#     print(Cookies().taobao_cookies())
