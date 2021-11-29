from setuptools import setup

with open("README.md","r") as fh:
      long_description=fh.read()

setup(name='cryptology',
      version='0.0.4',
      description='Decrypt/Encrypt text using various cipher techniques',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Antonio Felton',
      author_email='',
      py_modules=['crypto'],
      package_dir={'':'cryptology'}
)