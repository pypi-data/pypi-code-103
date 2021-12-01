# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['addonfactory_splunk_conf_parser_lib']
setup_kwargs = {
    'name': 'addonfactory-splunk-conf-parser-lib',
    'version': '0.3.4',
    'description': 'Splunk .conf files parser',
    'long_description': '# addonfactory_splunk_conf_parser_lib\n\nThis repository provides a one-file library to parse Splunk-specific `.conf` files.\n\nCurrently, it supports:\n\n1. Read/write .conf files with comments\n2. Additional comment prefix such as *\n3. Support multiline end with \\\n',
    'author': 'Splunk',
    'author_email': 'addonfactory@splunk.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/splunk/addonfactory-splunk-conf-parser-lib',
    'py_modules': modules,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
