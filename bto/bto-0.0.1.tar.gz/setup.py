from setuptools import setup, find_packages
import os


VERSION = '0.0.1'
DESCRIPTION = ''


# Setting up
setup(
    name="bto",
    version=VERSION,
    author="Divinemonk",
    author_email="<v1b7rc8eb@relay.firefox.com>",
    description=DESCRIPTION,
    packages=['bto'],
    py_modules = ['', ''],
    install_requires=['rich', 'termcolor'],
    keywords=['python', 'bytes', 'divinemonk', 'memory', 'cli', 'kb', 'mb', 'gb', 'size convertion'],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "typeffect=typeffect.__main__:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ]
)