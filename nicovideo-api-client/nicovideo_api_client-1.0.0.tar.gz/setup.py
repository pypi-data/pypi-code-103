# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nicovideo_api_client',
 'nicovideo_api_client.api',
 'nicovideo_api_client.api.v2']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0', 'urllib3>=1.26.6,<2.0.0']

setup_kwargs = {
    'name': 'nicovideo-api-client',
    'version': '1.0.0',
    'description': 'ニコニコ動画 スナップショット検索APIv2の Python クライアント',
    'long_description': '# NicoApiClient\n\n## 概要\n[ニコニコ動画 『スナップショット検索API v2』](https://site.nicovideo.jp/search-api-docs/snapshot) などの API について、仕様をなるべく意識せずに利用できるクライアントを提供する。\n\n## install\n\nPyPIリポジトリ: https://pypi.org/project/nicovideo-api-client/\n\n```shell\npip install nicovideo-api-client\n```\n\n### installed\n\n[![Downloads](https://pepy.tech/badge/nicovideo-api-client)](https://pepy.tech/project/nicovideo-api-client) [![Downloads](https://pepy.tech/badge/nicovideo-api-client/month)](https://pepy.tech/project/nicovideo-api-client) [![Downloads](https://pepy.tech/badge/nicovideo-api-client/week)](https://pepy.tech/project/nicovideo-api-client)\n\n### documentation\n\n[NicoApiClient コードドキュメント](https://javakky.github.io/NicoApiClientDocs/)\n\n## example\n\n```python\nfrom nicovideo_api_client.api.v2.snapshot_search_api_v2 import SnapshotSearchAPIV2\nfrom nicovideo_api_client.constants import FieldType\n\njson = SnapshotSearchAPIV2() \\\n    .tags_exact() \\\n    .query("VOCALOID") \\\n    .field({FieldType.TITLE, FieldType.CONTENT_ID}) \\\n    .sort(FieldType.VIEW_COUNTER) \\\n    .no_filter() \\\n    .limit(100) \\\n    .request() \\\n    .json()\n```\n\n## 利用規約\n\nhttps://site.nicovideo.jp/search-api-docs/snapshot#api%E5%88%A9%E7%94%A8%E8%A6%8F%E7%B4%84\n',
    'author': 'Javakky',
    'author_email': 'iemura.java@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Javakky/NicoApiClient',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
