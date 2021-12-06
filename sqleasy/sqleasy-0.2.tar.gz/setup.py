from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.2'
DESCRIPTION = 'A simple SQL system for beginners'

# Setting up
setup(
    name="sqleasy",
    version=VERSION,
    author="sk4yx",
    author_email="skayz.oficial3@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['sqlite3', 'os'],
    keywords=['python', 'sqlite', 'database', 'sql3', 'mysql', 'sqleasy'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)