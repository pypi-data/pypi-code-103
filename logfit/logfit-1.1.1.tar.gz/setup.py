# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from codecs import open
from os import path
import logfit

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='logfit',

    version=logfit.__version__,

    description='Watch and upload log files to log.fit',
    long_description=long_description,

    url='https://github.com/albertyw/logfit-daemon',

    author='Albert Wang',
    author_email='daemon@log.fit',

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Internet :: Log Analysis',
        'Topic :: System :: Logging',
        'Topic :: System :: Monitoring',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='logfit log.fit logging monitoring alerting',

    packages=find_packages(exclude=["logfit.tests"]),

    install_requires=[
        'requests',
        'rollbar',
        'python-magic',
        'pyyaml',
    ],

    test_suite="logfit.tests",

    # testing requires flake8 and coverage but they're listed separately
    # because they need to wrap setup.py
    extras_require={
        'dev': [
            'PyInstaller==3.2.1'
        ],
        'test': [],
    },

    package_data={},

    data_files=[],

    entry_points={
        'console_scripts': [
            'logfit=logfit.client:main',
        ],
    },
)
