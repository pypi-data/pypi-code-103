from setuptools import setup, find_packages
from modelchallangekleiner import version

setup(
    name="modelchallangekleiner",
    version=version,
    author="kleiner matias",
    description="model challange",
    packages=find_packages(),
    python_requires=">=3.8",
)
