"""
flask-eureka
-------------
flask extension that provides an interface to eureka via a flask.app
"""
import pathlib

from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='flask-eureka-client',
    version='1.0.1',
    author='IndustryApps',
    url='https://github.com/IndustryApps/flask-eureka',
    description="Eureka client library for flask",
    long_description=README,
    long_description_content_type="text/markdown",
    author_email="libin-p@industryapps.net",
    license="MIT",
    keywords=[
        'microservice',
        'netflix',
        'flask',
        'eureka',
        'industryapps'
    ],
    packages=find_packages(exclude=['tests*', 'examples*']),
    include_package_data=True,
    install_requires=['Flask', 'dnspython', 'urllib3'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
