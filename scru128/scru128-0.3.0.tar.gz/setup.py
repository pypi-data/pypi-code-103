# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scru128', 'scru128.cli']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['scru128 = scru128.cli:generate',
                     'scru128-inspect = scru128.cli:inspect']}

setup_kwargs = {
    'name': 'scru128',
    'version': '0.3.0',
    'description': 'SCRU128: Sortable, Clock and Random number-based Unique identifier',
    'long_description': '# SCRU128: Sortable, Clock and Random number-based Unique identifier\n\nSCRU128 ID is yet another attempt to supersede [UUID] in the use cases that need\ndecentralized, globally unique time-ordered identifiers. SCRU128 is inspired by\n[ULID] and [KSUID] and has the following features:\n\n- 128-bit unsigned integer type\n- Sortable by generation time (as integer and as text)\n- 26-digit case-insensitive portable textual representation\n- 44-bit biased millisecond timestamp that ensures remaining life of 550 years\n- Up to 268 million time-ordered but unpredictable unique IDs per millisecond\n- 84-bit _layered_ randomness for collision resistance\n\n```python\nfrom scru128 import scru128, scru128_string\n\n# generate a new identifier object\nx = scru128()\nprint(x)  # e.g. "00S6GVKR1MH58KE72EJD87SDOO"\nprint(int(x))  # as a 128-bit unsigned integer\n\n# generate a textual representation directly\nprint(scru128_string())  # e.g. "00S6GVKR3F7R79I72EJF0J4RGC"\n```\n\nSee [SCRU128 Specification] for details.\n\n[uuid]: https://en.wikipedia.org/wiki/Universally_unique_identifier\n[ulid]: https://github.com/ulid/spec\n[ksuid]: https://github.com/segmentio/ksuid\n[scru128 specification]: https://github.com/scru128/spec\n\n## Command-line interface\n\n`scru128` generates SCRU128 IDs.\n\n```bash\n$ scru128\n00PP7O1FIQFM7C7R8VBK61T94N\n$ scru128 -n 4\n00PP7OKSN7T37CR12PEIJILTA1\n00PP7OKSN7T37CT12PEJKN2BNO\n00PP7OKSN7T37CV12PEH41TP72\n00PP7OKSN7T37D112PEI1L0HMS\n```\n\n`scru128-inspect` prints the components of given SCRU128 IDs as human- and\nmachine-readable JSON objects.\n\n```bash\n$ scru128 -n 2 | scru128-inspect\n{\n  "input":        "00PP7OUAC22A7TO4VESB1R83L5",\n  "canonical":    "00PP7OUAC22A7TO4VESB1R83L5",\n  "timestampIso": "2021-10-02T23:38:47.832+00:00",\n  "timestamp":    "55381127832",\n  "counter":      "34770908",\n  "perSecRandom": "1306338",\n  "perGenRandom": "3283357349",\n  "fieldsHex":    ["00ce4f8f298", "2128fdc", "13eee2", "c3b40ea5"]\n}\n{\n  "input":        "00PP7OUAC22A7TQ4VES9SKQH9U",\n  "canonical":    "00PP7OUAC22A7TQ4VES9SKQH9U",\n  "timestampIso": "2021-10-02T23:38:47.832+00:00",\n  "timestamp":    "55381127832",\n  "counter":      "34770909",\n  "perSecRandom": "1306338",\n  "perGenRandom": "2035107134",\n  "fieldsHex":    ["00ce4f8f298", "2128fdd", "13eee2", "794d453e"]\n}\n```\n\n## License\n\nCopyright 2021 LiosK\n\nLicensed under the Apache License, Version 2.0 (the "License"); you may not use\nthis file except in compliance with the License. You may obtain a copy of the\nLicense at\n\nhttp://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in writing, software distributed\nunder the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR\nCONDITIONS OF ANY KIND, either express or implied. See the License for the\nspecific language governing permissions and limitations under the License.\n\n## See also\n\n- [scru128 - PyPI](https://pypi.org/project/scru128/)\n',
    'author': 'LiosK',
    'author_email': 'contact@mail.liosk.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/scru128/python',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7.12,<4.0.0',
}


setup(**setup_kwargs)
