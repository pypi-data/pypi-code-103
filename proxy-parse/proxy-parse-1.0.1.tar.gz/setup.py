# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['proxy_parse', 'proxy_parse.proxy', 'proxy_parse.spiders']

package_data = \
{'': ['*']}

install_requires = \
['Scrapy>=2.5.1,<3.0.0']

setup_kwargs = {
    'name': 'proxy-parse',
    'version': '1.0.1',
    'description': 'Easy-to-use sync library for handy parsing of proxies',
    'long_description': '<h1 align="center">\n  Proxy Parser\n</h1>\n\n## About\n\nSynchronous library, for convenient and fast parsing of proxies from different sources.\n\nUses Scrapy as a parser.\n\nAt the moment the library does not support automatic proxy check, this option will be added in the asynchronous version of the library.\n\n## Installation\nInstalling the latest version of the library:\n```shell\npip install proxy-parse\n```\n\n## Example\n\n```python\nfrom proxy_parse import ProxyParser\n\nproxy_parser = ProxyParser()\nproxies_list = proxy_parser.parse()\n```\n\n#### If you need, you can add some parameters to the ProxyParser class:\n\n- path_to_file - optional str parameter, the proxies will be saved to a file at the path\n- proxy_limit - optional int parameter, the ProxyParser.parse function will return as many proxies as you need\n- scrapy_spiders - optional scrapy.Spider list parameter, you can add your own spiders, which will work together with the others\n- scrapy_settings - optional dict parameter, you can replace the library rules with your own\n\n## Contribution\n\nAny changes from you will be good for the life of the library',
    'author': 'krilifon',
    'author_email': 'krilifongd@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/krilifon/proxy-parse',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
