import pathlib

from setuptools import find_namespace_packages, setup

HERE = pathlib.Path(__file__).parent
README = (HERE / 'README.md').read_text()

setup(
    name='mr_scraper',
    packages=find_namespace_packages(exclude=['build', 'dist', 'example', 'example.scrapers', 'tests']),
    version='0.4.0',
    description='Library to create scrapers in python',
    long_description=README,
    long_description_content_type='text/markdown',
    author='fernandojerez',
    license='Apache',
    requires=['webpilot', 'requests'],
    install_requires=['webpilot', 'requests'],
    test_suite='tests'
)
