import os

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

def package_files(directory):
  paths = []
  for (path, directories, filenames) in os.walk(directory):
    for filename in filenames:
      paths.append(os.path.join('..', path, filename))
  return paths


descriptor_files = package_files('kama_sdk/descriptors')
asset_files = package_files('kama_sdk/assets')

setuptools.setup(
  name="kama-sdk-py",
  version="0.0.27",
  author="NMachine",
  author_email="xavier@nmachine.io",
  description="SDK for the Kubernetes Application Management API (KAMA)",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/nectar-cs/kama-sdk-py",
  packages=setuptools.find_packages(exclude=["tests", "tests.*"]),
  package_data={
    '': descriptor_files + asset_files
    # 'kama_sdk': [
    #   'assets/*.*',
    #   'descriptors/**'
    # ]
  },
  include_package_data=True,
  install_requires=[
    'flask>=1.1',
    'flask-cors',
    'k8kat>=0.0.246',
    'requests',
    'termcolor>=1.1.0',
    'cachetools>=3.1',
    'redis>=3',
    'rq',
    'validators',
    'humanize>=3.2.0',
    'jq>=1.1.2',
    'sphinx>=4.1.2',
    'sphinx-rtd-theme',
    'python-docs-theme'
  ],
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  python_requires='>=3.8'
)
