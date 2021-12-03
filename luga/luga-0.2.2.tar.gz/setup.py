# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['luga']

package_data = \
{'': ['*']}

install_requires = \
['fasttext>=0.9.2,<0.10.0', 'httpx>=0.20.0,<0.21.0', 'numpy>=1.21,<2.0']

setup_kwargs = {
    'name': 'luga',
    'version': '0.2.2',
    'description': 'Sensing the language of the text using Machine Learning',
    'long_description': 'Luga\n==============================\n- A blazing fast language detection using fastText\'s language models\n\n![Languages](https://user-images.githubusercontent.com/14926709/143822756-8fd6437f-6c99-4a9f-9718-37f086955583.png)\n\n\n_Luga_ is a Swahili word for language. [fastText](https://github.com/facebookresearch/fastText) provides blazing-fast\nlanguage detection tool. Lamentably, [fastText\'s](https://fasttext.cc/docs/en/support.html) API is beauty-less and the documentation is a bit fuzzy.\nIt is also funky that we have to manually [download](https://fasttext.cc/docs/en/language-identification.html) and load models.\n\nHere is where _luga_ comes in. We abstract unnecessary steps and allow you to do precisely one thing: detecting text language.\n\n#### cover image\n[Stand Still. Stay Silent](http://sssscomic.com/index.php) - The relationships between Indo-European and Uralic languages by Minna Sundberg.\n\n### Show, don\'t tell\n![Luga in Action](example.gif)\n\n\n### Installation\n```bash\npython -m pip install -U luga\n```\n\n### Usage:\n⚠️ Note: The first usage downloads the model for you. It will take a bit longer to import depending on internet speed.\nIt is done only once.\n\n```python\nfrom luga import language\n\nprint(language("the world has ended yesterday"))\n\n# Language(name=\'en\', score=0.9804665446281433)\n```\n\n### Without Luga:\n\nDownload the model\n```bash\nwget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin -O /tmp/lid.176.bin\n```\n\nLoad and use\n```python\nimport fasttext\n\nPATH_TO_MODEL = \'/tmp/lid.176.bin\'\nfmodel = fasttext.load_model(PATH_TO_MODEL)\nfmodel.predict(["the world has ended yesterday"])\n\n# ([[\'__label__en\']], [array([0.98046654], dtype=float32)])\n```\n\n\n### Dev:\n\n```bash\npoetry run pre-commit install\n```\n\n## Release Flow\n```bash\n# assumes git push is completed\ngit tag -l #  lists tags\ngit tag v*.*.* # Major.Minor.Fix\ngit push origin tag v*.*.*\n\n# to delete tag:\ngit tag -d v*.*.* && git push origin tag -d v*.*.*\n```\n\n#### TODO:\n- [X] refactor artifacts.py\n- [X] auto checkers with pre-commit | invoke\n- [X] write more tests\n- [X] write github actions\n- [ ] create a smart data checker (a fast List[str], what do with none strings)\n- [ ] make it faster with Cython\n- [ ] get NDArray typing correctly\n- [ ] fix `artifacts.py` line 111 cast to List[str] that causes issues\n',
    'author': 'Prayson W. Daniel',
    'author_email': 'praysonwilfred@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Proteusiq/luga',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
