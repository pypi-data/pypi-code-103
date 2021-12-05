from setuptools import setup, find_packages


setup(
    name="find_palindromes",
    version="1.0",
    description="Пакет для нахождения палиндромов чисел в заданном диапазоне, с помощью операций Перевернуть и сложить",
    author="Eugene Martyshov",
    author_email="e.martyshov@yandex.ru",
    packages=find_packages(exclude=('package.tests*',)),
)
