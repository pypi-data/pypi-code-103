# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wit_core',
 'wit_core.api',
 'wit_core.cli',
 'wit_core.cli.initial_project.actions',
 'wit_core.cli.initial_project.templates',
 'wit_core.cli.initial_project.tests',
 'wit_core.core',
 'wit_core.tests']

package_data = \
{'': ['*'], 'wit_core.cli': ['initial_project/*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'click>=7.1.2,<8.0.0',
 'fastapi>=0.63.0,<0.64.0',
 'loguru>=0.5.3,<0.6.0',
 'pampy>=0.3.0,<0.4.0',
 'python-dotenv>=0.17.0,<0.18.0',
 'uvicorn>=0.13.4,<0.14.0',
 'wit>=6.0.0,<7.0.0']

entry_points = \
{'console_scripts': ['wit-core = wit_core.cli.cli:main']}

setup_kwargs = {
    'name': 'wit-core',
    'version': '0.1.6',
    'description': 'Response processor for wit.ai',
    'long_description': '# wit-core\n\nwit-core is a message processor for [wit.ai](wit.ai).\n\nHandle your intents by defining actions and responses.\n\n## Getting Started\n\n### Prerequisites\n\n- Python 3.6+\n\nInstall wheel package.\n\n```bash\npip install wheel\n```\n\n### Instalation\n\n```bash\npip install wit-core\n```\n\n## Documentation\n\n### Domain\n\nThe **domain.yaml** defines how the chatbot should operate according to the definition of the intents.\n\nIn the domain you specify the intents, actions and responses.\n\n```python\ngreet:\n    response: \n        text: "Hello, there!"\n\ntemperature_set:\n    action: action_temperature\n    response:\n        text: "The temperature was changed to {action_return}"\n\norder_pizza:\n    action: action_pizza\n    response:\n        template: template_pizza\n```\n\n### Actions\n\nActions are ways for you to write your own codes. For example, manipulating entities, make an API call, or to query a database.\n\n```python\ndef custom_action(resource):\n    temperature = resource.get_entity("wit$temperature")\n\n    return temperature.value\n```\n\nThe **resource** parameter allows accessing the properties of the wit.ai response.\n\n#### **Resource properties:**\n\n#### `get_latest_message`\n\nReturns the message sent by the user.\n\n#### `get_intent`\n\nReturns the properties of the intent.\n\n#### `get_entity("entity_name")`\n\nReturns the properties of the specified entity.\n\n#### `get_trait("trait_name")`\n\nReturns to the properties of the specified trait.\n\n### Responses\n\nIt is possible to define two types of responses: plain text and templates.\n\n#### **Text**\n\nYou can directly in the domain specify in the **response** a text response quickly.\n\n#### **Templates**\n\nTemplates serve to give you the possibility to add some logic to the answer. Templates receive the return value of an action.\n\n```python\ndef custom_template(action_return):\n    # Template logic...\n\n    return "Some response"\n```\n\n## Command Line Interface\n\n### `wit-core init`\n\nCreates the directory structure.\n\n### `wit-core shell`\n\nLoads the domain and allows interaction with the chatbot.\n\n### `wit-core http-server`\n\nCreates a http server that can be used for custom integrations. They provide a URL where you can post messages.\n\n### `wit-core websocket-server`\n\nCreate a websocket server for real-time interaction with the chatbot. They provide an endpoint where you can send messages.\n\n## How to use\n\nCreates the folder structure needed for the project.\n\n```bash\nwit-core init\n```\n\nCreate a .env at the root of the application with your secret wit.ai key.\n\n```bash\n# Wit.ai\nACCESS_TOKEN=YOUR-SECRET-KEY\n```\n\nInteract with the chatbot.\n\n```bash\nwit-core shell\n```\n\n## Contributing\n\n1. Fork it (<https://github.com/yourname/yourproject/fork>)\n2. Create your feature branch (`git checkout -b feature/fooBar`)\n3. Commit your changes (`git commit -am \'Add some fooBar\'`)\n4. Push to the branch (`git push origin feature/fooBar`)\n5. Create a new Pull Request\n\n## Development\n\nClone the repository:\n\n```bash\ngit clone https://github.com/LucasOliveiraS/wit-core\n```\n\nInstall the dependencies:\n\n```bash\npoetry install\n```\n\nRun tests:\n\n```bash\nmake tests\n```\n',
    'author': 'Lucas Oliveira',
    'author_email': 'ls.oliveiras.santos@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/LucasOliveiraS/wit-core',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>3.6.1,<4',
}


setup(**setup_kwargs)
