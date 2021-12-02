# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['abuse_whois',
 'abuse_whois.api',
 'abuse_whois.api.endpoints',
 'abuse_whois.matchers',
 'abuse_whois.matchers.shared_hosting',
 'abuse_whois.matchers.whois',
 'abuse_whois.schemas']

package_data = \
{'': ['*'],
 'abuse_whois.matchers.shared_hosting': ['rules/*'],
 'abuse_whois.matchers.whois': ['rules/*']}

install_requires = \
['email-validator>=1.1.3,<2.0.0',
 'fastapi>=0.70.0,<0.71.0',
 'loguru>=0.5.3,<0.6.0',
 'pydantic>=1.8.2,<2.0.0',
 'pyhumps>=3.0.2,<4.0.0',
 'sh>=1.14.2,<2.0.0',
 'tldextract>=3.1.2,<4.0.0',
 'typer>=0.4.0,<0.5.0',
 'uvicorn[standard]>=0.15.0,<0.16.0',
 'whois-parser>=0.1.3,<0.2.0']

entry_points = \
{'console_scripts': ['abuse_whois = abuse_whois.cli:app']}

setup_kwargs = {
    'name': 'abuse-whois',
    'version': '0.1.0',
    'description': 'Find where to report a domain for abuse',
    'long_description': '# abuse_whois\n\nYet another way to find where to report a domain for abuse.\n\nThis tool is highly inspired from the following libraries:\n\n- https://github.com/bradleyjkemp/abwhose\n- https://github.com/certsocietegenerale/abuse_finder\n\n## Requirements\n\n- Python 3.7+\n- whois\n\n## Installation\n\n```bash\npip install abuse_whois\n```\n\n## Usage\n\n### As a library\n\n```python\nfrom abuse_whois import get_get_abuse_contacts\n\nget_abuse_contacts("1.1.1.1")\nget_abuse_contacts("github.com")\nget_abuse_contacts("https://github.com")\nget_abuse_contacts("foo@example.com")\n```\n\n### As a CLI tool\n\n```bash\n$ abuse_whois 1.1.1.1 | jq .\n{\n  "address": "1.1.1.1",\n  "hostname": "1.1.1.1",\n  "ipAddress": "1.1.1.1",\n  "sharedHostingProvider": null,\n  "registrar": null,\n  "hostingProvider": {\n    "provider": "Cloudflare",\n    "address": "https://www.cloudflare.com/abuse/form",\n    "type": "form"\n  }\n}\n```\n\n### As a REST API\n\n```bash\n$ uvicorn abuse_whois.api.app:app\nINFO:     Started server process [2283]\nINFO:     Waiting for application startup.\nINFO:     Application startup complete.\nINFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)\n\n$ http localhost:8000/api/whois/ address=https://github.com\n{\n    "address": "https://github.com",\n    "hostingProvider": {\n        "address": "abuse@amazonaws.com",\n        "provider": "",\n        "type": "email"\n    },\n    "hostname": "github.com",\n    "ipAddress": "52.192.72.89",\n    "registrar": {\n        "address": "abusecomplaints@markmonitor.com",\n        "provider": "MarkMonitor, Inc.",\n        "type": "email"\n    },\n    "sharedHostingProvider": null\n}\n```\n',
    'author': 'Manabu Niseki',
    'author_email': 'manabu.niseki@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ninoseki/abuse_whois',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
