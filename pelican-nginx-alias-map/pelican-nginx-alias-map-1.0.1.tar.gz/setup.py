# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pelican', 'pelican.plugins.nginx_alias_map']

package_data = \
{'': ['*'], 'pelican.plugins.nginx_alias_map': ['test_data/*']}

install_requires = \
['pelican>=4.5']

extras_require = \
{'markdown': ['markdown>=3.2,!=3.3.5']}

setup_kwargs = {
    'name': 'pelican-nginx-alias-map',
    'version': '1.0.1',
    'description': 'This Pelican plugin creates an nginx-compatible map between the final page locations and prior locations, defined in the `Alias` attribute for any article or page.',
    'long_description': 'nginx_alias_map: A Plugin for Pelican\n====================================================\n\n[![Build Status](https://img.shields.io/github/workflow/status/gaige/nginx_alias_map/build)](https://github.com/gaige/nginx_alias_map/actions)\n[![PyPI Version](https://img.shields.io/pypi/v/pelican-nginx-alias-map)](https://pypi.org/project/pelican-nginx-alias-map/)\n![License](https://img.shields.io/pypi/l/pelican-nginx-alias-map?color=blue)\n\n\nThis Pelican plugin creates an nginx-compatible map between the final page locations\nand prior locations, defined in the "Alias" attribute for any article or page.\n\nLoosely based on [pelican-alias](https://github.com/Nitron/pelican-alias) by Chris Williams,\nwhich itself was inspired by jekyll_alias_generator.\n\nInstallation\n------------\n\nThis plugin can be installed via:\n\n    python -m pip install pelican-nginx-alias-map\n\nUsage\n-----\n\nAdd the directory to the base plugins directory to `PLUGIN_PATHS` in\n`pelicanconf.py`, and then add `nginx_alias_map` to the `PLUGINS` list. For example,\n\n    PLUGIN_PATHS = ["plugins"]\n    PLUGINS = [\'nginx_alias_map\']\n\nDefinable parameters (with defaults in brackets) allow some configuration of the output\nof the plugin.\n\nThere are two definable parameters, one from Chris\'s code (`ALIAS_DELIMITER`), which\ndefines the delimiter for multiple aliases for the same item; and `ALIAS_FILE`, which\ndefines the final name of the output file containing the map; and\n\n    ALIAS_DELIMITER : Delimeter between multiple aliases for the same item [","]\n    ALIAS_FILE : Name of map file to be placed in `output` [\'alias_map.txt\']\n    ALIAS_MAP : Name of the map used in the alias file [\'redirect_uri\']\n    ALIAS_MAP_TEMP: Name of the map used in the alias file when 2-stage lookup is needed [\'redirect_uri_1\']\n\n### Support for URLs with query strings\n\nIn the event that you need to redirect a URI that contains a query string, a separate\nmap block will be created to map the `$request_uri` against an re.escaped version of your\nalias that contains the `?` character. Otherwise, when no query string is present, the\ntest is made against `$uri`, which has much more processing done with it (query string\nremoval, removal of unnecessary \'/\'s, and so forth).\n\n### NGINX configuration\n\nThe resulting file (stored in `output/$(ALIAS_FILE)`) is ready to be included into\nyour nginx configuration file (in an http stanza). Once the map is created, use the\n`ALIAS_MAP` variable in your processing.\n\n    include /opt/web/output/alias_map.txt;\n\n    server {\n      listen       *:80 ssl;\n      server_name  example.server;\n\n\n        # Redirection logic\n        if ( $redirect_uri ) {\n            return 301 $redirect_uri;\n        }\n\n        location / {\n            alias /opt/web/output;\n        }\n    }\n\nThis configuration uses the evil `if` statement, but it\'s concise.  If you have a better\napproach, please create a pull request, and I\'ll add it to this doc (or replace it if it\nmakes more sense).\n\nI\'ve chosen to use a 301 redirect here, because I\'m confident of the permanency.  During\ntesting, you may want to use a 302.\n\nContributing\n------------\n\nContributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues][].\n\nTo start contributing to this plugin, review the [Contributing to Pelican][] documentation, beginning with the **Contributing Code** section.\n\n[existing issues]: https://github.com/gaige/nginx_alias_map/issues\n[Contributing to Pelican]: https://docs.getpelican.com/en/latest/contribute.html\n\nLicense\n-------\n\nThis project is licensed under the MIT license.\n',
    'author': 'Gaige B. Paulsen',
    'author_email': 'gaige@cluetrust.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gaige/nginx_alias_map',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
