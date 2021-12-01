# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ddrr', 'ddrr.templatetags']

package_data = \
{'': ['*'], 'ddrr': ['templates/ddrr/*']}

install_requires = \
['Django>=2.2', 'attrs>=19.1']

extras_require = \
{'xml': ['lxml>=4.6.3,<5.0.0']}

setup_kwargs = {
    'name': 'ddrr',
    'version': '3.0.0',
    'description': 'Print request and response headers, body (with pretty-printing), etc.',
    'long_description': '# Django Debug Requests & Responses (DDRR)\n\nGet more out of your `runserver` development output! Print request and response\nheaders, body (with pretty-printing), etc.  Highly customizable! Supports\nDjango 2.2+ and 3.0+, with Python 3.7+.\n\n- Full request headers\n- The entire request body\n- Pretty-printing optional\n- Colored output\n- Super easy setup\n- No extra dependencies\n\nDDRR can also be used for general logging with some configuration of your own.\n\n## Installation\n\n1. ```\n   $ pip install ddrr\n   ```\n\n2. Add `"ddrr"` to `INSTALLED_APPS`\n\n3. Insert `"ddrr.middleware.DebugRequestsResponses"` first in `MIDDLEWARE`\n\n**Done!** When you run `runserver`, you\'ll now get the entire HTTP requests and\nresponses, including headers and bodies.\n\nIf you don\'t like the default output format, read on...\n\n## Customization\n\n```python\nDDRR = {\n    "ENABLE_REQUESTS": True,  # enable request logging\n    "ENABLE_RESPONSES": True,  # enable response logging\n    "LEVEL": "DEBUG",  # ddrr log level\n    "PRETTY_PRINT": False,  # pretty-print JSON and XML\n    "REQUEST_TEMPLATE_NAME": "ddrr/default-request.html",  # request log template name\n    "REQUEST_TEMPLATE": None,  # request log template string (overrides template name)\n    "RESPONSE_TEMPLATE_NAME": "ddrr/default-response.html",  # response log template name\n    "RESPONSE_TEMPLATE": None,  # response log template string (overrides template name)\n    "REQUEST_HANDLER": logging.StreamHandler(),  # request log handler\n    "RESPONSE_HANDLER": logging.StreamHandler(),  # response log handler\n    "ENABLE_COLORS": True,  # enable colors if terminal supports it\n    "LIMIT_BODY": None,  # limit request/response body output to X chars\n    "DISABLE_DJANGO_SERVER_LOG": False,  # disable default django server log\n}\n```\n\n### Template contexts\n\nIf you want to customize request or response templates, you can use the following values:\n\n- **Request template context:**\n  - `ddrr.body` - request body\n  - `ddrr.content_type` - request content type\n  - `ddrr.formatter` - the formatter\n  - `ddrr.headers` - mapping of header fields and values\n  - `ddrr.method` - request method\n  - `ddrr.path` - request path\n  - `ddrr.query_params` - query parameters\n  - `ddrr.query_string` - query string\n  - `ddrr.record` - the actual log record object\n  - `ddrr.request` - the actual request object\n- **Response template context:**\n  - `ddrr.content` - response content\n  - `ddrr.content_type` - response content type\n  - `ddrr.formatter` - the formatter\n  - `ddrr.headers` - mapping of header fields and values\n  - `ddrr.reason_phrase` - response reason phrase\n  - `ddrr.record` - the actual log record object\n  - `ddrr.response` - the actual response object\n  - `ddrr.status_code` - response status code\n\nFor example, this will log the method, path and body of each request, as well\nas the status code, reason phrase and content of each response:\n\n```python\nDDRR = {\n    "REQUEST_TEMPLATE": "{{ ddrr.method }} {{ ddrr.path }}\\n"\n                        "{{ ddrr.body }}",\n    "RESPONSE_TEMPLATE": "{{ ddrr.status_code }} {{ ddrr.reason_phrase }}\\n"\n                         "{{ ddrr.content }}",\n}\n```\n\n### Pretty-printing\n\nBy default, pretty-printing is disabled.  Set `DDRR["PRETTY_PRINT"]` to `True`\nto enable it.\n\nPretty-printing of JSON requires no external dependency.\n\nPretty-printing of XML uses `minidom` by default and doesn\'t require any extra\ndependency. If you want to use `lxml` instead, which is slightly better at\npretty-printing XML, you can install that using `pip install ddrr[xml]`.\n\n## How it works internally\n\nThe middleware `ddrr.middleware.DebugRequestsResponses` sends the entire\nrequest object as the message to `ddrr-request-logger`.  This logger has been\nconfigured to use `ddrr.formatters.DjangoTemplateRequestFormatter` which\ninternally uses Django\'s built-in template engine to format the request into\nhuman-readable form. By default, this is shown in your console output, but you\ncan easily configure it to log it to a file, Logstash, or anything else.\n\n## Similar projects\n\n- [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io)\n\n## Development and contributions\n\nPR\'s are always welcome!\n\nFor hacking on DDRR, make sure you are familiar with:\n\n- [Black](https://github.com/ambv/black)\n- [Flake8](http://flake8.pycqa.org/)\n- [Poetry](https://poetry.eustace.io/)\n- [pre-commit](https://github.com/pre-commit/pre-commit)\n- [pytest](https://docs.pytest.org)\n\nInstall dependencies and set up the pre-commit hooks.\n\n```\n$ poetry install\n$ pre-commit install\n```\n\nThe pre-commit hooks will, among other things, run Flake8 on the code base and\nBlack to make sure the code style is consistent across all files.  Check out\n[`.pre-commit-config.yaml`](.pre-commit-config.yaml) for details.\n',
    'author': 'Deniz Dogan',
    'author_email': 'denizdogan@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/denizdogan/django-debug-requests-responses',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
