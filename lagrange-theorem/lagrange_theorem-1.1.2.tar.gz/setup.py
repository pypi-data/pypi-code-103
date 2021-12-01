from setuptools import setup, find_packages

setup(
    name='lagrange_theorem',
    version='1.1.2',
    author='Dima Skorobogatov',
    author_email='dima.skorobogatov.99@mail.ru',
    description='Decomposition of numbers into the sum of four squares',
    long_description=open('README.txt').read(),
    packages=find_packages(),
    install_requires=['pytest']
)
