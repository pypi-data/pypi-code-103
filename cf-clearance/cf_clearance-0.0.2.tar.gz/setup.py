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
    'version': '0.0.2',
    'description': 'Purpose To make a cloudflare challenge pass successfully, Can be use cf_clearance bypassed by cloudflare, However, with the cf_clearance, make sure you use the same IP and UA as when you got it.',
    'long_description': '# cf_clearance\nReference from [playwright_stealth](https://github.com/AtuboDad/playwright_stealth) and [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)\n\nPurpose To make a cloudflare challenge pass successfully, Can be use cf_clearance bypassed by cloudflare, However, with the cf_clearance, make sure you use the same IP and UA as when you got it.\n\n## Warning\nPlease use interface mode, You must add headless=False.  \nIf you use it on linux or docker, use XVFB.\n\n## Install\n\n```\n$ pip install cf_clearance\n```\n\n## Usage\n### sync\n```python\nfrom playwright.sync_api import sync_playwright\nfrom cf_clearance import sync_retry, stealth_sync\n\nwith sync_playwright() as p:\n    browser = p.chromium.launch(headless=False)\n    page = browser.new_page()\n    stealth_sync(page)\n    page.goto(\'https://nowsecure.nl\')\n    res = sync_retry(page)\n    if res:\n        cppkies = page.context.cookies()\n        for cookie in cppkies:\n            if cookie.get(\'name\') == \'cf_clearance\':\n                print(cookie.get(\'value\'))\n        ua = page.evaluate(\'() => {return navigator.userAgent}\')\n        print(ua)\n    else:\n        print("fail")\n    browser.close()\n```\n### async\n```python\nimport asyncio\nfrom playwright.async_api import async_playwright\nfrom cf_clearance import async_retry, stealth_async\n\nasync def main():\n    async with async_playwright() as p:\n        browser = await p.chromium.launch(headless=False)\n        page = await browser.new_page()\n        await stealth_async(page)\n        await page.goto(\'https://nowsecure.nl\')\n        res = await async_retry(page)\n        if res:\n            cppkies = await page.context.cookies()\n            for cookie in cppkies:\n                if cookie.get(\'name\') == \'cf_clearance\':\n                    print(cookie.get(\'value\'))\n            ua = await page.evaluate(\'() => {return navigator.userAgent}\')\n            print(ua)\n        else:\n            print("fail")\n        await browser.close()\n\n\nasyncio.get_event_loop().run_until_complete(main())\n```',
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
