# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['proxygrab',
 'proxygrab.package',
 'proxygrab.package.api',
 'proxygrab.package.scrappers']

package_data = \
{'': ['*']}

install_requires = \
['aiodns==3.0.0',
 'aiohttp==3.8.1',
 'beautifulsoup4==4.10.0',
 'cchardet==2.1.7',
 'click==8.0.3',
 'lxml==4.6.4',
 'ujson>=4.3.0,<5.0.0']

entry_points = \
{'console_scripts': ['proxygrab = proxygrab.cmdline:clicmd']}

setup_kwargs = {
    'name': 'proxygrab',
    'version': '1.2.0',
    'description': 'Asynchronous Library to scrap proxies for my web scrapping applications and other testing purposes',
    'long_description': '# ProxyGrab\n\n<p align="center">\n<a href="https://proxygrab.netlify.com"><img src="https://raw.githubusercontent.com/Divkix/ProxyGrab/master/docs/img/name.png"></a>\n<i>Software to scrap proxies for my web scrapping and other testing purposes.</i></br></br>\n<a href="https://pypi.org/project/ProxyGrab/"><img src="https://img.shields.io/pypi/v/ProxyGrab" alt="PyPI"></a>\n<a href="https://github.com/Divkix/ProxyGrab/actions"><img src="https://github.com/Divkix/ProxyGrab/workflows/CI%20%28pip%29/badge.svg" alt="CI (pip)"></a>\n<a href="https://www.codacy.com/gh/Divkix/ProxyGrab/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Divkix/ProxyGrab&amp;utm_campaign=Badge_Grade"><img src="https://app.codacy.com/project/badge/Grade/b5b68ed7f04c4f639bef56df0668d289"/></a>\n<a href="https://pypi.org/project/proxygrab/"><img src="https://img.shields.io/pypi/pyversions/ProxyGrab.svg" alt="Supported Python Versions"></a>\n<a href="https://pepy.tech/project/ProxyGrab"><img src="https://pepy.tech/badge/ProxyGrab" alt="Downloads"></a>\n</p>\n\nI made this software to scrap proxies for my web scrapping and other testing purposes. This program just uses [aiohttp](https://pypi.org/project/aiohttp/) to get the response from API and return the proxies, also it can scrape proxies from a few sites so that it can be used without using the API.\n\n<i><b>NOTE:</b> This library isn\'t designed for production use. It\'s advised to use your own proxies or purchase a service which provides an API. These are merely free ones that are retrieved from sites and should only be used for development or testing purposes.</br>\n\n\n## Installation\n\nThe latest version of proxygrab is available via `pip`:\n\n```shell\npip install --upgrade proxygrab\n```\n\n## Provided Proxies\n\n<table style="width:100%">\n  <tr>\n    <th>Provider</th>\n    <th>Proxy Types avaiable</th>\n    <th>Url</th>\n  </tr>\n  <tr>\n    <td>Proxyscrape</td>\n    <td>http, https, socks4, socks5</td>\n    <td>https://proxyscrape.com/</td>\n  </tr>\n  <tr>\n    <td>Proxy-List</td>\n    <td>http, https, socks4, socks5</td>\n    <td>https://www.proxy-list.download/</td>\n  </tr>\n  <tr>\n    <td>SSL Proxies</td>\n    <td>https</td>\n    <td>https://www.sslproxies.org/</td>\n  </tr>\n  <tr>\n    <td>Free Proxy List</td>\n    <td>http, https</td>\n    <td>https://free-proxy-list.net/</td>\n  </tr>\n  <tr>\n    <td>US Proxies</td>\n    <td>http, https</td>\n    <td>https://www.us-proxy.org/</td>\n  </tr>\n  <tr>\n    <td>Socks Proxy</td>\n    <td>socks4, socks5</td>\n    <td>https://www.socks-proxy.net/</td>\n  </tr>\n</table>\n\n## Documentation\n\nhttps://proxygrab.vercel.app\n\n## Contribuiting\n\nWanna help and improve this project?\n\nMake sure to follow these before opening a PR:\n\n- Make sure your PR passes the test and is formatted according to pre-commit.\n- Make sure the package is working without any issues!\n\n## License\n\nThis project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details\n\n## Thanks to\n\n- [@JaredLGillespie](https://github.com/JaredLGillespie) for his [proxyscrape library](https://github.com/JaredLGillespie/proxyscrape) from which I took scrappers!\n- Proxy Providers mentioned above\n',
    'author': 'Divkix',
    'author_email': 'techdroidroot@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Divkix/ProxyGrab',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
