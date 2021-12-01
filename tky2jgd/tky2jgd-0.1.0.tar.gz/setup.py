# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['tky2jgd']
setup_kwargs = {
    'name': 'tky2jgd',
    'version': '0.1.0',
    'description': 'Python port of TKY2JGD to transform coordinates from Tokyo Datum (EPSG:4301) to JGD2000 (EPSG:4612)',
    'long_description': '# TKY2JGD\n\n国土地理院のTKY2JGDをPythonに移植したものです。\n\nオリジナルのTKY2JGDは<http://vldb.gsi.go.jp/sokuchi/tky2jgd/download/down.cgi>からダウンロードできます。\n\n座標変換パラメータファイル`data/TKY2JGD.par`はv2.1.1を使用しています。\n\n## Usage\n\n```\n$ python3 tky2jgd.py 36.103774791666666 140.08785504166664\n36.10696628160147 140.08457686629436\n```\n\n```\n>>> import tky2jgd\n>>> tky2jgd.load_parameter("data/TKY2JGD.par")\n>>> lat, lon = 36.103774791666666, 140.08785504166664\n>>> dB, dL = tky2jgd.bilinear(lat, lon)\n>>> lat += dB / 3600\n>>> lon += dL / 3600\n>>> print(lat, lon)\n36.10696628160147 140.08457686629436\n```\n',
    'author': 'TAKAHASHI Shuuji',
    'author_email': 'shuuji3@gmail.com',
    'maintainer': 'TAKAHASHI Shuuji',
    'maintainer_email': 'shuuji3@gmail.com',
    'url': 'https://github.com/shuuji3/TKY2JGD',
    'py_modules': modules,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
