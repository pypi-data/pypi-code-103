#encoding: utf-8
import io

from swagger2case import __version__
from setuptools import find_packages, setup

with io.open("README.md", encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='swagger2case',
    version=__version__,
    description='Convert SWAGGER data to JSON testcases for HttpRunner.',
    long_description=long_description,
    long_description_content_type='text/markdown',  # Optional (see note above)
    author='贝克街的捉虫师',
    author_email='forpeng@foxmail.com',
    url='https://github.com/BSTester/swagger2case',
    license='MIT',
    packages=find_packages(exclude=['test.*', 'test']),
    package_data={},
    keywords='swagger converter json',
    install_requires=["jsonschema"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    entry_points={
        'console_scripts': [
            'sw2case=swagger2case.cli:main'
        ]
    }
)
