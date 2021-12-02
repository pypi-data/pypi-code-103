import os

from setuptools import find_namespace_packages, setup

from src.kivy_history import version


def read(fn):
    with open(os.path.join(os.path.dirname(__file__), fn)) as f:
        return f.read()


# exposing the params so it can be imported
setup_params = {
    'name': 'kivy_history',
    'version': version.__version__,
    'description': 'kivy history inspired on javascript history api',
    'long_description': read('README.md'),
    'long_description_content_type': 'text/markdown',
    'author': 'Fernando Morente',
    'url': 'https://github.com/gmork2/kivy-history',
    'packages': find_namespace_packages(where='src'),
    'package_dir': {'': 'src'},
    'entry_points': {
        'console_scripts': ['kivy-history=kivy_history.sample:main'],
    },
    'keywords': 'kivy, history',
    'python_requires': '>=3',
    'install_requires': [
        'kivy',
    ],
}


def run_setup():
    setup(**setup_params)


# makes sure the setup doesn't run at import time
if __name__ == '__main__':
    run_setup()
