from setuptools import setup
from setuptools import find_packages

setup(name = 'genagg',
      version = '0.0.1',
      packages = find_packages(),
      install_requires = ['torch','torch_scatter'],
      author = 'Ryan Kortvelesy',
      author_email = 'rk627@cam.ac.uk',
      description = 'A Learnable, Generalised Aggregation Module',
)