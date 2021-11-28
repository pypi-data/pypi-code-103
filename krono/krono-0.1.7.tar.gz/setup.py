# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['krono']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.3.3,<2.0.0', 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['krono = krono.main:app']}

setup_kwargs = {
    'name': 'krono',
    'version': '0.1.7',
    'description': 'Aplicativo de linha de comando para rastrear o tempo de trabalho',
    'long_description': '# Krono\n\nKrono é um aplicativo de linha de comando para rastrear tempo e gerar relatórios em formato de fatura.\n\n## Instalação\n\nUtilize o package manager [pip](https://pip.pypa.io/en/stable/) para instalar o krono.\n\n```bash\npip install krono\n```\n\n## Utilização\n\nPara iniciar a contagem de horas é preciso rodar o comando `track`\ninformado o nome da atividade em que se está trabalhando\n\n```shell\nkrono track "Nome da atividade"\n```\n\nPara gerar uma fatura, é preciso utilizar o comando `report` informando a data de início do relatório \nno formato `%Y-%m-%d`\n\n```shell\nkrono report -s "2021-11-01"\n```\n\nMais informações estão disponíveis ao rodar o comando\n\n```shell\nkrono --help\n```\n\n## Utilizando um arquivo de configuração\n\nA fim de facilitar a utilização, é possível criar um arquivo de configuração na pasta raiz do projeto \nchamado `rastreador.json`, com as variáveis de valor hora (`hourly_rate`), solicitante (`requested_from`) e\nsolicitado (`bill_to`)\n\n```json\n{\n  "hourly_rate": 1000,\n  "requested_from": "rafael.matsumoto@catolicasc.org.br",\n  "bill_to": "catolicasc@catolicasc.org.br"\n}\n```\n\n## Licença\n[MIT](https://choosealicense.com/licenses/mit/)',
    'author': 'rafaelmatsumoto',
    'author_email': 'rafael.matsumoto43@catolicasc.edu.br',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
