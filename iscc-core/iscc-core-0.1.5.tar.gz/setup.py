# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['iscc_core']

package_data = \
{'': ['*']}

install_requires = \
['Pillow',
 'bitarray-hardbyte',
 'blake3',
 'more-itertools',
 'pydantic>=1.8.2,<2.0.0',
 'uvarint>=1.2.0,<2.0.0',
 'xxhash']

extras_require = \
{'turbo': ['cython', 'pybase64']}

setup_kwargs = {
    'name': 'iscc-core',
    'version': '0.1.5',
    'description': 'ISCC - Core Algorithms',
    'long_description': '# iscc-core - ISCC Core Algorithms\n\n[![Build](https://github.com/iscc/iscc-core/actions/workflows/tests.yml/badge.svg)](https://github.com/iscc/iscc-core/actions/workflows/tests.yml)\n[![Version](https://img.shields.io/pypi/v/iscc-core.svg)](https://pypi.python.org/pypi/iscc-core/)\n[![Downloads](https://pepy.tech/badge/iscc-core)](https://pepy.tech/project/iscc-core)\n\n> **iscc-core** is a Python library that implements the core algorithms of [ISCC v1.1](https://iscc.codes)\n(International Standard Content Code)\n\n## What is ISCC\n\nThe **ISCC** (*International Standard Content Code*) is an identifier for digital media\nassets.\n\nAn **ISCC** is derived algorithmically from the digital content itself, just like\ncryptographic hashes. However, instead of using a single cryptographic hash function to\nidentify data only, the ISCC uses a variety of algorithms to create a composite\nidentifier that exhibits similarity-preserving properties (soft hash).\n\nThe component-based structure of the ISCC identifies content at multiple levels of\nabstraction. Each component is self-describing, modular and can be used separately or\nin conjunction with others to aid in various content identification tasks.\n\nThe algorithmic design supports scenarios that require content deduplication, database\nsynchronisation and indexing, integrity verification, timestamping, versioning, data\nprovenance, similarity clustering, anomaly detection, usage tracking, allocation of\nroyalties, fact-checking and general digital asset management use-cases.\n\n## What is `iscc-core`\n\n`iscc-core` is the python based library of the core algorithms to create standard\ncompliant **ISCC** codes. It also serves as a reference for porting ISCC to other\nprogramming languages.\n\n## ISCC Architecture\n\n![ISCC Architecure](https://raw.githubusercontent.com/iscc/iscc-core/master/docs/images/iscc-architecture.png)\n\n## Installation\n\nUse the package manager [pip](https://pip.pypa.io/en/stable/) to install `iscc-core`.\n\n```bash\npip install iscc-core\n```\n\n## Quick Start\n\n```python\nfrom iscc_core import (\n    gen_meta_code,\n    gen_image_code,\n    gen_data_code,\n    gen_instance_code,\n    gen_iscc_code,\n)\n\nimage_path = "../docs/images/iscc-architecture.png"\n\nmeta_code = gen_meta_code(\n    title="ISCC Architecure",\n    extra="A schematic overview of the ISCC"\n)\n\nprint("Meta-Code:\\t\\t", meta_code.code)\nprint("Structure:\\t\\t", meta_code.code_obj.explain, end="\\n\\n")\n\nwith open(image_path, "rb") as stream:\n\n    image_code = gen_image_code(stream)\n    print("Image-Code:\\t\\t", image_code.code)\n    print("Structure:\\t\\t", image_code.code_obj.explain, end="\\n\\n")\n\n    stream.seek(0)\n    data_code = gen_data_code(stream)\n    print("Data-Code:\\t\\t", data_code.code)\n    print("Structure:\\t\\t", data_code.code_obj.explain, end="\\n\\n")\n\n    stream.seek(0)\n    instance_code = gen_instance_code(stream)\n    print("Instance-Code:\\t", instance_code.code)\n    print("Structure:\\t\\t", instance_code.code_obj.explain, end="\\n\\n")\n\niscc_code = gen_iscc_code((meta_code.code, image_code.code, data_code.code, instance_code.code))\nprint("Canonical ISCC:\\t ISCC:{}".format(iscc_code.code))\nprint("Structure:\\t\\t", iscc_code.explain)\n```\n\nThe output of this example is as follows:\n\n```\nMeta-Code:      AAA5H3V6SZHWDUKX\nStructure:      META-NONE-V0-64-d3eebe964f61d157\n\nImage-Code:     EEA34YXAFUJWOZ5Q\nStructure:      CONTENT-IMAGE-V0-64-be62e02d136767b0\n\nData-Code:      GAA6JYHWISAVU77Z\nStructure:      DATA-NONE-V0-64-e4e0f644815a7ff9\n\nInstance-Code:  IAAUULVLVWQLXSEM\nStructure:      INSTANCE-NONE-V0-64-4a2eabada0bbc88c\n\nISCC-CODE:      ISCC:KED5H3V6SZHWDUKXXZROALITM5T3BZHA6ZCICWT77FFC5K5NUC54RDA\nStructure:      ISCC-IMAGE-V0-256-d3eebe964f61d157be62e02d136767b0e4e0f644815a7ff94a2eabada0bbc88c\n```\n\n## Documentation\n\nhttps://iscc-core.iscc.codes\n\n## Project Status\n\nISCC is in the process of being standardized within\n[ISO/TC 46/SC 9](https://www.iso.org/standard/77899.html).\n\n## Maintainers\n[@titusz](https://github.com/titusz)\n\n## Contributing\n\nPull requests are welcome. For major changes, please open an issue first to discuss\nwhat you would like to change. Please make sure to update tests as appropriate.\n\nYou may also want join our developer chat on Telegram at <https://t.me/iscc_dev>.\n\n\n## Changelog\n\n### [0.1.5] - 2021-11-28\n\n- Fix documentation\n- Change metahash creation logic\n- Refactor models\n- Add Content-Code-Mixed\n- Add ISCC-ID\n- Refactor `compose` to `gen_iscc_code`\n- Refactor `models` to `schema`\n\n### [0.1.4] - 2021-11-17\n- Simplified options\n- Optimize video WTA-hash for use with 64-bit granular features\n\n### [0.1.3] - 2021-11-15\n- Try to compile Cython/C accelerator modules when installing via pip\n- Simplify soft_hash api return values\n- Add .code() method to InstanceHasher, DataHasher\n- Remove granular fingerprint calculation\n- Add more top-level imports\n\n### [0.1.2] - 2021-11-14\n- Export more functions to toplevel\n- Return schema driven objects from ISCC code generators.\n\n### [0.1.1] - 2021-11-14\n- Fix packaging problems\n\n### [0.1.0] - 2021-11-13\n- Initial release\n\n\n',
    'author': 'Titusz',
    'author_email': 'tp@py7.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/iscc/iscc-core',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
