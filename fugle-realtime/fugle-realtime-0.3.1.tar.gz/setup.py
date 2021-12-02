# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fugle_realtime',
 'fugle_realtime.http_client',
 'fugle_realtime.websocket_client']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0', 'websocket-client>=1.2.1,<2.0.0']

setup_kwargs = {
    'name': 'fugle-realtime',
    'version': '0.3.1',
    'description': 'Fugle Realtime API client library for Python',
    'long_description': "# Fugle Realtime\n\n[![PyPI version][pypi-image]][pypi-url]\n[![Python version][python-image]][python-url]\n[![Build Status][action-image]][action-url]\n\n> Fugle Realtime API client library for Python\n\n## Install\n\n```sh\n$ pip install fugle-realtime\n```\n\n## Usage\n\nThe library a Python client that supports HTTP API and WebSocket.\n\n### HTTP API\n\n```py\nfrom fugle_realtime import HttpClient\n\napi_client = HttpClient(api_token='demo')\n```\n\n#### intraday.meta\n\n```py\napi_client.intraday.meta(symbolId='2884')\n```\n\n#### intraday.quote\n\n```py\napi_client.intraday.quote(symbolId='2884')\n```\n\n#### intraday.chart\n\n```py\napi_client.intraday.chart(symbolId='2884')\n```\n\n#### intraday.dealts\n\n```py\napi_client.intraday.dealts(symbolId='2884', limit=50)\n```\n\n#### intraday.volumes\n\n```py\napi_client.intraday.volumes(symbolId='2884')\n```\n\n### Simple WebSocket Demo\n\n```py\nimport time\nfrom fugle_realtime import WebSocketClient\n\ndef handle_message(message):\n    print(message)\n\ndef main():\n    ws_client = WebSocketClient(api_token='demo')\n    ws = ws_client.intraday.quote(symbolId='2884', on_message=handle_message)\n    ws.run_async()\n    time.sleep(3)\n    ws.close()\n\nif __name__ == '__main__':\n    main()\n```\n\n## Reference\n\n[Fugle Realtime API](https://developer.fugle.tw)\n\n## License\n\n[MIT](LICENSE)\n\n[pypi-image]: https://img.shields.io/pypi/v/fugle-realtime\n[pypi-url]: https://pypi.org/project/fugle-realtime\n[python-image]: https://img.shields.io/pypi/pyversions/fugle-realtime\n[python-url]: https://pypi.org/project/fugle-realtime\n[action-image]: https://img.shields.io/github/workflow/status/fugle-dev/fugle-realtime-py/Run%20Tests/next\n[action-url]: https://github.com/fugle-dev/fugle-realtime-py/actions/workflows/pytest.yml\n",
    'author': 'Fortuna Intelligence Co., Ltd.',
    'author_email': 'development@fugle.tw',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fugle-dev/fugle-realtime-py#readme',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
