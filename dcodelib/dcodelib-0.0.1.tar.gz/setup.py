
import os
import sys
from pathlib import Path
from setuptools import setup, find_packages


if sys.version_info.major != 3:
    raise RuntimeError("This package requires Python 3+")


version = '0.0.1'
pkg_name = 'dcodelib'
gitrepo = 'trisongz/dcodelib'
root = Path(__file__).parent

requirements = [
    'pylogz',
    'pyyaml',
    'typer',
    'boltons'
]

args = {
    'packages': find_packages(include = ['dcode', 'dcode.*']),
    'install_requires': requirements,
    'long_description': root.joinpath('README.md').read_text(encoding='utf-8'),
    'python_requires': '>=3.6',
    'entry_points': {
        'console_scripts': [
            'dcode = dcode.cli:mainCli',
        ],
    }
}

setup(
    name=pkg_name,
    version=version,
    url='https://github.com/trisongz/dcodelib',
    license='MIT Style',
    description='Collection of various serialization methods with cli',
    author='Tri Songz',
    author_email='ts@growthengineai.com',
    long_description_content_type="text/markdown",
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
    ],
    **args
)