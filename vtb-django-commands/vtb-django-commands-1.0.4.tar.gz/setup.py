"""
Описание установки
"""
import io
from pathlib import Path
from setuptools import setup, find_packages

"""
python -m pip install --upgrade setuptools wheel twine
python setup.py sdist bdist_wheel

python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
python -m twine upload dist/*
export CURL_CA_BUNDLE="" && python -m twine upload --repository-url https://nexus-ci.corp.dev.vtb/repository/puos-pypi-lib/ dist/*
"""


here = Path(__file__).parent

REQUIRED = [
    'django>=3.0.0',
    'djangorestframework>=3.12.2',
    'vtb-authorizer-utils>=0.0.17',
    'vtb-http-interaction>=0.1.4',
    'vtb-django-utils'
]

with io.open(here / 'README.md', encoding='utf-8') as f:
    long_description = '\n' + f.read()

about = {}
with open(here / 'vtb_django_commands' / '__about__.py') as fp:
    exec(fp.read(), about)


setup(
    name=about['__title__'],
    version=about['__version__'],
    description='Django commands',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=about['__author__'],
    author_email=about['__email__'],
    packages=find_packages(exclude=['tests']),
    install_requires=REQUIRED,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Framework :: Django :: 3.0",
        "Operating System :: OS Independent",
    ],
    extras_require={
        'test': [
            'pytest',
            'pytest-env',
            'pylint',
        ]
    }
)
