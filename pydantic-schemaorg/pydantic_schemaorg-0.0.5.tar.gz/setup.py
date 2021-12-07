# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydantic_schemaorg']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'pydantic-schemaorg',
    'version': '0.0.5',
    'description': 'Pydantic classes for Schema.org',
    'long_description': '# pydantic_schemaorg\n\nUse [Schema.org](https://schema.org) types in [pydantic](https://pydantic-docs.helpmanual.io/)! <br> <br>\n**Pydantic_schemaorg** contains all the models defined by schema.org. The pydantic classes are auto-generated from the\nschema.org model definitions that can be found\non [https://schema.org/version/latest/schemaorg-current-https.jsonld](https://schema.org/version/latest/schemaorg-current-https.jsonld)\n\n## How to install\n\n```pip install pydantic_schemaorg```<br><br>\nImport any class you want to use by with the following convention<br>\n```from pydantic_schemaorg.<SCHEMAORG_MODEL_NAME> import <SCHEMAORG_MODEL_NAME>```<br><br>\n\nA full (hierarchical) list of Schema.org model names can be found [here](https://schema.org/docs/full.html)\n\n## Example usages\n\n```\nfrom datetime import datetime\nfrom pydantic_schemaorg.ScholarlyArticle import ScholarlyArticle\n\nscholarly_article = ScholarlyArticle(url=\'https://github.com/lexiq-legal/pydantic_schemaorg\',\n                                    sameAs=\'https://github.com/lexiq-legal/pydantic_schemaorg\',\n                                    copyrightNotice=\'Free to use under the MIT license\',\n                                    dateCreated=datetime.now())\nprint(scholarly_article.json(exclude_none=True))\n```\n\n```{"url": "https://github.com/lexiq-legal/pydantic_schemaorg", "sameAs": "https://github.com/lexiq-legal/pydantic_schemaorg", "@type": "ScholarlyArticle", "copyrightNotice": "Free to use under the MIT license", "dateCreated": "2021-11-30T17:31:38.454252"}```',
    'author': 'Reinoud Baker',
    'author_email': 'reinoud@lexiq.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lexiq-legal/pydantic_schemaorg',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
}


setup(**setup_kwargs)
