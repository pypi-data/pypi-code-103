# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['cortex_xdr_client',
 'cortex_xdr_client.api',
 'cortex_xdr_client.api.models',
 'cortex_xdr_client.api.utils']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'cortex-xdr-client',
    'version': '1.0.2',
    'description': 'API client for Cortex XDR Prevent',
    'long_description': '# cortex-xdr-client\n\nA python-based API client for [Cortex XDR API](https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api).\n\nCurrently, it supports the following Cortex XDR **Prevent** APIs:\n- [Get Incidents](https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/incident-management/get-incidents.html)\n- [Get Extra Incident Data](https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/incident-management/get-extra-incident-data.html)\n- [Get Alerts](https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/incident-management/get-alerts.html)\n- [Get All Endpoints](https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/endpoint-management/get-all-endpoints.html)\n- [Get Endpoint](https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/endpoint-management/get-endpoints.html)\n- [Isolate Endpoints](https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/response-actions/isolate-endpoints.html)\n- [Scan Endpoints](https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/response-actions/scan-endpoints.html)\n\n',
    'author': 'ebarti',
    'author_email': 'me@eloibarti.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ebarti/cortex-xdr-client',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
