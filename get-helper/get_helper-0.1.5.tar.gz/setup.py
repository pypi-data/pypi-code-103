from setuptools import setup, find_packages

setup(
      name='get_helper',
      version='0.1.5',
      description='Library module for getting a response using requests',
      packages=find_packages(include=['get_helper']),
      author='AlexeiSimonov',
      author_email='sushka2820655@yandex.ru',
      license='MIT',
      install_requires=[
            'requests'
      ]
)
