# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cf_clearance']

package_data = \
{'': ['*'], 'cf_clearance': ['js/*']}

install_requires = \
['playwright>=1.17.0,<2.0.0']

setup_kwargs = {
    'name': 'cf-clearance',
    'version': '0.0.3',
    'description': 'Purpose To make a cloudflare challenge pass successfully, Can be use cf_clearance bypassed by cloudflare, However, with the cf_clearance, make sure you use the same IP and UA as when you got it.',
    'long_description': '# cf_clearance\nReference from [playwright_stealth](https://github.com/AtuboDad/playwright_stealth) and [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)\n\nPurpose To make a cloudflare challenge pass successfully, Can be use cf_clearance bypassed by cloudflare, However, with the cf_clearance, make sure you use the same IP and UA as when you got it.\n\n## Warning\nPlease use interface mode, You must add headless=False.  \nIf you use it on linux or docker, use XVFB.\n\n## Install\n\n```\n$ pip install cf_clearance\n```\n\n## Usage\n### sync\n```python\nfrom playwright.sync_api import sync_playwright\nfrom cf_clearance import sync_retry, stealth_sync\nimport requests\n\nproxies = {\n    "all": "socks5://localhost:7890"\n}\nres = requests.get(\'https://nowsecure.nl\', proxies=proxies)\nif \'<title>Please Wait... | Cloudflare</title>\' in res.text:\n    print("cf challenge fail")\nwith sync_playwright() as p:\n    browser = p.chromium.launch(headless=False, proxy={"server": "socks5://localhost:7890"})\n    page = browser.new_page()\n    stealth_sync(page)\n    page.goto(\'https://nowsecure.nl\')\n    res = sync_retry(page)\n    if res:\n        cookies = page.context.cookies()\n        for cookie in cookies:\n            if cookie.get(\'name\') == \'cf_clearance\':\n                cf_clearance_value = cookie.get(\'value\')\n                print(cf_clearance_value)\n        ua = page.evaluate(\'() => {return navigator.userAgent}\')\n        print(ua)\n    else:\n        print("cf challenge fail")\n    browser.close()\nheaders = {"user-agent": ua}\ncookies = {"cf_clearance": cf_clearance_value}\nres = requests.get(\'https://nowsecure.nl\', proxies=proxies, headers=headers, cookies=cookies)\nif \'<title>Please Wait... | Cloudflare</title>\' not in res.text:\n    print("cf challenge success")\n```\n### async\n```python\nimport asyncio\nfrom playwright.async_api import async_playwright\nfrom cf_clearance import async_retry, stealth_async\nimport requests\n\n\nasync def main():\n    proxies = {\n        "all": "socks5://localhost:7890"\n    }\n    res = requests.get(\'https://nowsecure.nl\', proxies=proxies)\n    if \'<title>Please Wait... | Cloudflare</title>\' in res.text:\n        print("cf challenge fail")\n    async with async_playwright() as p:\n        browser = await p.chromium.launch(headless=False, proxy={"server": "socks5://localhost:7890"})\n        page = await browser.new_page()\n        await stealth_async(page)\n        await page.goto(\'https://nowsecure.nl\')\n        res = await async_retry(page)\n        if res:\n            cookies = await page.context.cookies()\n            for cookie in cookies:\n                if cookie.get(\'name\') == \'cf_clearance\':\n                    cf_clearance_value = cookie.get(\'value\')\n                    print(cf_clearance_value)\n            ua = await page.evaluate(\'() => {return navigator.userAgent}\')\n            print(ua)\n        else:\n            print("cf challenge fail")\n        await browser.close()\n    headers = {"user-agent": ua}\n    cookies = {"cf_clearance": cf_clearance_value}\n    res = requests.get(\'https://nowsecure.nl\', proxies=proxies, headers=headers, cookies=cookies)\n    if \'<title>Please Wait... | Cloudflare</title>\' not in res.text:\n        print("cf challenge success")\n\nasyncio.get_event_loop().run_until_complete(main())\n```',
    'author': 'vvanglro',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vvanglro/cf_clearance',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
