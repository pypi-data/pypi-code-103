# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
import os

here = os.path.abspath(os.path.dirname(__file__))
version = '0.1'

# with open(path.join(here, 'README.md'), encoding='utf-8') as f:
#    long_description = f.read()
long_description = "See website for more info."

setup(
    name='pywscat',
    version=version,
    description='Simple Websocket Netcat thing',
    long_description=long_description,
    url='https://github.com/bannsec/wscat',
    author='Michael Bann',
    author_email='self@bannsecurity.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console'
    ],
    keywords='python3 websockets netcat',
    packages=["pywscat"],
    install_requires=['websockets'],
    entry_points={
        'console_scripts': [
            'wscat = pywscat.cli:main',
            'pywscat = pywscat.cli:main',
        ],
    },
)
