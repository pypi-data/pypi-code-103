from setuptools import setup, find_packages

with open("README.md","r") as fh:
      long_description=fh.read()

setup(name='cryptology',
      version='0.0.13',
      description='Decrypt/Encrypt text using various cipher techniques',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Antonio Felton',
      packages=find_packages()
)