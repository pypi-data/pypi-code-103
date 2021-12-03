import typing as t
from os import path

from pkg_resources import parse_requirements
from setuptools import find_packages
from setuptools import setup

import ingot_redis as package


URL = ""
ROOT_DIR = path.abspath(path.dirname(__file__))
readme_filename = "README.md"
requirements_file = "requirements.txt"


def get_readme() -> str:
    """get_readme.

    Extracts content from the README.mg file for long description.
    """
    with open(path.join(ROOT_DIR, readme_filename)) as _file:
        return _file.read()


def get_requirements() -> t.List[str]:
    """get_requirements.

    Extracts requirements from the requirements.txt file.
    """
    with open(path.join(ROOT_DIR, requirements_file)) as _file:
        return list((str(req) for req in parse_requirements(_file)))


setup(
    name=package.NAME,
    description=package.DESCRIPTION,
    long_description=get_readme(),
    long_description_content_type="text/markdown",
    version=package.VERSION,
    url=URL,
    author=package.AUTHOR,
    author_email=package.AUTHOR_EMAIL,
    packages=find_packages(),
    include_package_data=True,
    install_requires=get_requirements(),
    entry_points={
        "console_scripts": ["ingot-redis-cli = ingot_redis.scripts.ingot_redis:main []"]
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Web Environment",
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet",
    ],
)
