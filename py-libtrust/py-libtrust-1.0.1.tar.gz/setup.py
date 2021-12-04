# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['libtrust', 'libtrust.keys']

package_data = \
{'': ['*']}

install_requires = \
['cryptography>=3.0.0', 'typing-extensions>=4.0.1,<5.0.0']

setup_kwargs = {
    'name': 'py-libtrust',
    'version': '1.0.1',
    'description': 'Yet another docker/libtrust implement by python.',
    'long_description': '# libtrust - Yet another docker/libtrust implement by python.\n\nLibtrust is library for managing authentication and authorization using public key cryptography.\n\nWorks for Python 3.6+.\n\n## Usage\n\n### Install\nYou can install from PyPi.\n\n```bash\n❯ pip install py-libtrust\n```\n\n### Example\n#### Sign/Verify a jose-json-web-signature\n```python\nimport datetime\nfrom libtrust.keys.ec_key import generate_private_key\nfrom libtrust.jsonsign import JSONSignature\n\n# Generate a EC P256 private key\nec_key = generate_private_key("P-256")\n\nyour_content = {\n    "author": "shabbywu(shabbywu@qq.com)"\n}\n\n# New a JSONSignature\njs = JSONSignature.new(your_content)\n\n# signature\njs.sign(ec_key, dt=datetime.datetime.utcfromtimestamp(0))\n\njws = js.to_jws()\n\nloaded_js = JSONSignature.from_jws(jws)\n\nassert js == loaded_js\nassert js.verify() == loaded_js.verify()\n```\n\n#### Serialize/Deserialize a self-signed JSON signature\n```python\nimport json\nimport datetime\nfrom libtrust.keys.ec_key import generate_private_key\nfrom libtrust.jsonsign import JSONSignature\n\n# Generate a EC P256 private key\nec_key = generate_private_key("P-256")\n\nyour_content = {\n    "author": "shabbywu(shabbywu@qq.com)"\n}\n\n# New a JSONSignature\njs = JSONSignature.new(your_content)\n\n# signature\njs.sign(ec_key, dt=datetime.datetime.utcfromtimestamp(0))\n\npretty_signature = js.to_pretty_signature("signatures")\nloaded_js = js.from_pretty_signature(pretty_signature)\n\nassert js.verify() == loaded_js.verify()\nassert json.loads(pretty_signature)["author"] == "shabbywu(shabbywu@qq.com)"\n```\n\n## Copyright and license\n\nCode and documentation copyright 2021 shabbywu(shabbywu@qq.com).\nCode released under the Apache 2.0 license.\n\n## Reference\n\n- [docker/libtrust](https://github.com/distribution/distribution/tree/main/vendor/github.com/docker/libtrust)\n- [realityone/libtrust-py](https://github.com/realityone/libtrust-py)\n',
    'author': 'shabbywu',
    'author_email': 'shabbywu@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/shabbywu/libtrust',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
