# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['invoicepy', 'invoicepy.cli', 'invoicepy.config']

package_data = \
{'': ['*'], 'invoicepy': ['schema/*', 'templates/*']}

install_requires = \
['Click>=7.0,<8.0',
 'Jinja2>=3.0.0,<4.0.0',
 'pydantic[email]>=1.8.0,<2.0.0',
 'weasyprint>=53.0,<54.0']

entry_points = \
{'console_scripts': ['invoicepy = invoicepy.cli.main:cli']}

setup_kwargs = {
    'name': 'invoicepy',
    'version': '0.1.2',
    'description': 'invoicepy is a simple cli tool for generating and storing invoices.',
    'long_description': 'invoicepy\n=========\n<img src="https://repository-images.githubusercontent.com/430929750/36502a64-8878-4341-a38b-11a2f1b78155" alt="invoice" width="666"/>\n\n**CLI** invoice tool, store and print invoices as *pdf*. save companies and\ncustomers for later use.\n\n\ninstallation\n------------\n\n``` {.sourceCode .bash}\npip install invoicepy\n```\n> *see troubleshooting section below for common problems*\n\nconfig\n------\n\n[config](src/invoicepy/schema/config.json) stores `companies` and `customers` by alias and [invoices](src/invoicepy/schema/invoice.json).\n`custom_templates_dir` is available for customising templates.\n\nwrite [sample config](src/invoicepy/config/sample_config.json) with:\n``` {.sourceCode .bash}\ninvoicepy sample-config\n# then customize it in $HOME/.invoicepy.conf\n```\n\nexamples\n--------\n\n1. print pdf saving it in current directory, result is invoice nr. BAR001\n``` {.sourceCode .bash}\ninvoicepy pdf --company foo --customer bar --line \'{"price":10, "qty": 20, "name":"1h services"}\' --series BAR\n```\n<img src="examples/2021-11-23_bar-inc_bar1.png" alt="invoice" width="400"/>\n\nwhen above is repeated twice, the invoices numers will increase, BAR002, BAR003. this is calculated per series.\nsee below for more options.\n\n2. below example won\'t save invoice in config, open in it browser and use custom template specified in `custom_templates_dir`:\n```\ninvoicepy pdf --company foo --customer bar --line ... -b --no-save --series BAR --number 25 --curency USD --template my_custom_template.html\n```\n\ncli\n---\n\n``` {.sourceCode .}\ninvoicepy [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  -C, --config PATH\n  --help             Show this message and exit.\n\nCommands:\nsample-config        generate sample config in home dir\npdf                  prints pdf to given path\n```\n\n**pdf**\n\n```\nOptions:\n  -l, --line TEXT       json string of invoice line, can pass multiple. ex:\n                        --line \'{"price":15, "qty": 100, "name":"1h cleaning\n                        services", "vat": 21}\' --line ...  [required]\n\n\t\t\tThe fields are as follows:\n\t\t\t`price` - price of product\n\t\t\t`qty` - quantity of product\n\t\t\t`name` - name of product\n\t\t\t`vat` - vat rate %\n\n\n  -c, --company TEXT    company alias as in configuration.  [required]\n  -r, --customer TEXT   customer alias as in configuration.  [required]\n  -d, --date TEXT       invoice date, `create_date` field.\n  -e, --due-date TEXT   If due date is not provided, `payment_term_days` is\n                        used to calculate it.\n\n  -s, --series TEXT     invoice series  [required]\n  -n, --number INTEGER  invoice number, if not provided, it will calculated\n                        from company config for given series.\n\n  -u, --currency TEXT   currency, default=EUR\n  -o, --output PATH     output path, can be new filepath, directory. If it\'s\n                        not provided the invoice pdf will be saved in current\n                        directory.\n\n  -t, --template TEXT   template name, ex. simple.html. `custom_templates_dir`\n                        will be searched first, then package templates.\n\n  --save / --no-save    decides whether to store invoice in config file.\n  -b, --browser         open generated invoice in browser.\n  --help                show this message and exit.\n```\n\ntemplates\n---------\ncurrently two templates are available:\n- `simple.html` - simple english template (*default*).\n- `simple_lt.html` - simple lithuanian/english template.\n\nyou can pass your own template name with `-t`. see `custom_templates_dir` (config section). have a look on schema below in case you want to write your own templates. templates are written in html and use [jinja2](https://jinja.palletsprojects.com/en/3.0.x/) templating language.\n\nschema\n------\n-   [schema/invoice.json](src/invoicepy/schema/invoice.json)\n-   [schema/config.json](src/invoicepy/schema/config.json)\n\n\ntroubleshooting\n---------------\n\n| Problem|Solution|\n|--------|--------|\n| `invoicepy: command not found`| Your distro didn\'t append python bin folder to your PATH. You can check where package lives with `pip3 show invoicepy` and add appropriate path. Example in your .bashrc: `export PATH="$PATH:$HOME/.local/bin"`|\n|`OSError: encoder jpeg2k not available`| This is caused by pillow needing some extra libs, on Ubuntu: `sudo apt-get install libjpeg8-dev` then `pip install --no-cache-dir -I pillow`. On other distros find `libjpeg8-dev` equiavilent or google around for solutions regarding pillow.|\n|`sample-config` says `Aborting` and exists| Fixed in `0.1.1`|\n\ncontributing\n------------\n\nif you written cool new template or improved some features, feel free to fork and PR. See [contributing guidelines](CONTRIBUTING.md).\n\nto-dos\n------\n\n-   use babel for translations and locale\n-   extend tests\n-   consider moving config to yaml\n-   backup copy config on start\n-   invoices should have unique ids (maybe companies and customers too?)\n-   view saved invoices\n-   reprint saved invoices (?)\n-   package for arch (AUR)\n\nCredits\n-------\n\nThis package was created with\n[Cookiecutter](https://github.com/audreyr/cookiecutter) and the\n[johanvergeer/cookiecutter-poetry](https://github.com/johanvergeer/cookiecutter-poetry)\nproject template.\n\nTemplate taken from here and slightly modified:\n<https://github.com/sparksuite/simple-html-invoice-template>\n\nLicence\n-------\n\nFree software: MIT license\n',
    'author': 'Adam W.',
    'author_email': 'adam1edinburgh@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/adamwojt/invoicepy',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
