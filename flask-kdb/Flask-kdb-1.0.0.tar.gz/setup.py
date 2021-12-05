import os
import sys
from setuptools import find_packages, setup

from version import __version__

BASEDIR = os.path.dirname(__file__)

requirements = [
    'Flask>=2.0.2',
    'qPython3>=1.0.0',
    'numpy>=1.8.0'
]

setup(
    name='Flask-kdb',
    url='http://www.github.com/ryanmcfarland/flask-kdb/',
    author='Ryan McFarland',
    author_email='ryanmcfarland@outlook.com',
    description='kdb+ connections within a Flask application.',
    long_description=open(os.path.join(BASEDIR, 'readme.md')).read(),
    long_description_content_type='text/markdown',
    version=__version__,
    license='MIT License',
    keywords=['flask', 'kdb', 'kdb+', 'q', 'qpython'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Framework :: Flask',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development',
    ],
    include_package_data=True,
    packages=find_packages(exclude=("tests",)),
    install_requires=requirements,
)