# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kbgetter']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.10.0,<5.0.0',
 'requests>=2.26.0,<3.0.0',
 'tinydb>=4.5.2,<5.0.0']

setup_kwargs = {
    'name': 'kbgetter',
    'version': '0.1.5',
    'description': 'Download FreshService articles to a local machine',
    'long_description': 'README.rst\n===========\nFSGetter is used to pull FreshService knowledgebase articles to a local machine.\n\nDocumentation home: https://kbgetter.readthedocs.io/en/latest/\nInstall: \n\n.. code-block::\n\n\tpip install kbgetter\n\t\nExamples\n---------\n\n1. Create database, articles and local articles.\n\n.. code-block::\n\n\tfrom kbgetter import FSGetter\n\n\t#Please get your API key by following the instructions at https://api.freshservice.com/#authentication\n\t#username must be the API key. username/password is no longer supported\n\tapi_key = \'your_api_key\'\n\t#password will always be \'X\' for API key usernames\n\tpassword = \'X\'\n\t#kb_url is the base instance of FreshService for an organization\n\tkb_url = \'https://mycompany.freshservice.com\'\n\t#kb_name, in this example, is the directory where this script and KBgetter.py is stored and is a relative path\n\tkb_name = \'./\'\n\t#current_categories is passed to make_articles to limit the articles created by category\n\t#the categories\' IDs (integers) listed here are the categories that have D365 and associated systems documentation\n\tcurrent_categories = [523212, 523213, 523214]\n\n\tkb = FSGetter(api_key,password,kb_url,\'./\')\n\tbuilder = kb.build_kb()\n\t#passing current_categories to make_articles limits the articles created by category.\n\t#if nothing is passed to make_articles all articles in solutions will be created.\n\tmake_articles = kb.make_articles(current_categories)\n\tprint(\'%s articles created\'%make_articles)\n\tmake_local = kb.make_local_articles()\n\tprint(\'%s local articles created\'%make_local)\n\n2. View all categories from the database.\n\n.. code-block::\n\n\tfrom tinydb import TinyDB\n\tdb = TinyDB(\'db.json\')\n\tcategories = db.table(\'categories\')\n\tfor category in categories:\n\t\tinput("ID = %s, Name = %s, Description = %s"%(category[\'id\'],category[\'name\'],category[\'description\']))\n\n',
    'author': 'Matt Kasfeldt',
    'author_email': 'matt.kasfeldt@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mkasfeldt/KBgetter',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
