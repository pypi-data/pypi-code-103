from distutils.core import setup
from setuptools import find_packages

with open("README.md") as f:
    long_description = f.read()

setup(name='sam-learner',
      version='2.1.3',
      python_requires=">=3.8",
      description='Safe Action Model Learner',
      long_description=long_description,
      long_description_content_type="text/markdown",
      keywords="automatic safe action model learning",
      author='Argaman Mordoch',
      packages=find_packages(exclude=["tests", "utils"]),
     )