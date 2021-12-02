import re

from setuptools import setup


PACKAGE_NAME = "anomalo"


def get_version():
    try:
        f = open(f"{PACKAGE_NAME}/_version.py")
    except EnvironmentError:
        return None
    for line in f.readlines():
        mo = re.match('__version__ = "([^\']+)"', line)
        if mo:
            ver = mo.group(1)
            return ver
    return None


setup(
    name="anomalo",
    version=get_version(),
    description="Python bindings for the Anomalo API",
    long_description="A basic REST API client and command line client for Anomalo",
    url="https://anomalo.com",
    author="Anomalo",
    author_email="support@anomalo.com",
    license="license.txt",
    packages=[PACKAGE_NAME],
    install_requires=["requests", "fire"],
    tests_require=[],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "anomalo = anomalo:main",
        ]
    },
)
