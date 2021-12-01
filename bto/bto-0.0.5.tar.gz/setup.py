from setuptools import setup, find_packages
import os


VERSION = '0.0.5'
DESCRIPTION = ''


# Setting up
setup(
    name="bto",
    version=VERSION,
    author="Divinemonk",
    author_email="<v1b7rc8eb@relay.firefox.com>",
    description=DESCRIPTION,
    packages=['bto'],
    py_modules = ['methods'],
    install_requires=['rich', 'termcolor', 'psutil', 'getmac'],
    keywords=['python', 'bytes', 'divinemonk', 'memory', 'cli', 'kb', 'mb', 'gb', 'size convertion'],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "bto=bto.__main__:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ]
)