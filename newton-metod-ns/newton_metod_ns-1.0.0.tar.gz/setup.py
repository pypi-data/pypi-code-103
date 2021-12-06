from io import open
from setuptools import setup

"""
:authors: NikitaSamarin
"""
version = '1.0.0'
with open("README.txt") as f:
    long_description = f.read()
setup(
    name = 'newton_metod_ns',
    version = version,
    author = 'NikitaSamarin',
    author_email = 'yormungandsam@yandex.ru',
    description = "Newton's method python module",
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    packages = ['newton_metod_ns'],
    install_requires = ['sympy','fire','pytest'])
