import setuptools
from setuptools import setup
import subprocess
import os

name = "numops"
assert name.lower() in os.listdir("."), "Please name the directory with same name as that of pypi package"

# version = subprocess.run(['git', 'describe', '--tags'], stdout=subprocess.PIPE).stdout.decode("utf-8").strip()
version = "0.0.3"
print(version)

with open("README.md", "r") as fh:
    long_description = fh.read()

description = 'The project is to automtically publish to pypi on creation of release tag in git repo'

setup(
  name = name,                              # How you named your package folder
  packages = setuptools.find_packages(),    # Chose the same as "name"
  version = version,                        # Start with a small number and increase it with every change you make
  license='MIT',                            # Choose a license from here: https://help.github.com/articles/licensing-a-repository
  description = description,                # Give a short description about your library
  long_description = long_description,
  long_description_content_type="text/markdown",
  author = 'Vivek Yadav',                   
  author_email = 'vivekkya@gmail.com',      
  url = 'https://github.com/vivekkya/auto-release-to-pypi.git', # Provide either the link to your github or to your website
  download_url = f'https://github.com/vivekkya/auto-release-to-pypi/archive/refs/tags/{version}.tar.gz',
  keywords = ['Github Actions', 'PYPI', 'Github Release'],   # Keywords that define your package best
  install_requires=[                                         
          'numpy'
      ],
  setup_requires=['pytest-runner', 'flake8', 'argparse'],
  tests_require=['pytest'],
  # extras_require={'interactive': ['matplotlib>=2.2.0', 'jupyter']},
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)