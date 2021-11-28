"""
Pip.Services MySQL
------------------

Pip.Services is an open-source library of basic microservices.
pip_services3_mysqlb provides MySQL persistence components.

Links
`````

* `website <http://github.com/pip-services/pip-services>`_
* `development version <http://github.com/pip-services3-python/pip-services3-mysql-python>`

"""

try:
    readme = open('readme.md').read()
except:
    readme = __doc__

from setuptools import find_packages
from setuptools import setup

setup(
    name='pip_services3_mysql',
    version='3.2.5',
    url='http://github.com/pip-services3-python/pip-services3-mysql-python',
    license='MIT',
    author='Conceptual Vision Consulting LLC',
    author_email='seroukhov@gmail.com',
    description='Mysql persistence components for Pip.Services in Python',
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=['config', 'data', 'test']),
    include_package_data=True,
    zip_safe=True,
    platforms='any',
    install_requires=[
        'mysql-connector-python',
        'pip-services3-commons >= 3.3.9, < 4.0',
        'pip-services3-components >= 3.5.0, < 4.0',
        'pip_services3_data >= 3.2.3, < 4.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
