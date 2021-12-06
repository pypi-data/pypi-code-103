from setuptools import setup
from setuptools import find_packages


setup(
    name='count_sort',
    version='1.0',
    description='Пакет для сортировки чисел методом подсчета',
    author='Шестера Дмитрий',
    author_email='typa_lya@mail.ru',
    packages=find_packages(exclude=('packages.tests*',)),
    )
