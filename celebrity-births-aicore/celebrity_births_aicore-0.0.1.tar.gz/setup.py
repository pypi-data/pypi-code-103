from setuptools import setup
from setuptools import find_packages

setup(
    name='celebrity_births_aicore',
    version='0.0.1',
    description='Mock package that allows you to find celebrity by date of birth',
    url='https://github.com/IvanYingX/project_structure_pypi.git',
    author='Ivan Ying',
    license='MIT',
    packages=find_packages(),
    install_requires=['requests', 'beautifulsoup4'],
)
