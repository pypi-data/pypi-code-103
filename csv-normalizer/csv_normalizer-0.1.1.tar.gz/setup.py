#! python3
# pylint: disable=invalid-name
"""
 Setup file
 Help from: http://www.scotttorborg.com/python-packaging/minimal.html
 https://docs.python.org/3/distutils/commandref.html#sdist-cmd
 https://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
 https://docs.python.org/3.4/tutorial/modules.html
 Local Install it with python setup.py install
 Or use: python setup.py develop (changes to the source files will be
 immediately available)
 https://pypi.python.org/pypi?%3Aaction=list_classifiers
"""
import os
from src import __version__
from os import path
from setuptools import setup, find_packages

here_path = path.abspath(path.dirname(__file__))

with open(os.path.join(here_path, 'requirements.txt')) as f:
    requires = [x.strip() for x in f if x.strip()]

# Get the version from __init__ source file
mypackage_root_dir = 'src'
version = __version__

# Get the long description from the relevant file
readme_path = path.join(here_path, 'README.md')
with open(readme_path, encoding='utf-8') as f:
    long_description = f.read()

# Define setuptools specifications
setup(name='csv_normalizer',
      version=version,
      description='csv normalize to have always same output csv',
      long_description_content_type="text/markdown",
      long_description=long_description,  # this is the file README.md
      # https://pypi.org/classifiers/
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: System Administrators',
          'Topic :: Utilities',
          'Intended Audience :: Telecommunications Industry',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3 :: Only'
      ],
      url='https://github.com/CoffeeITWorks/csv_normalizer',
      author='Pablo Estigarribia',
      author_email='pablodav@gmail.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      package_data={
          'data': ['src/dummy/*'],
          'normalizer_process_png': ['csv_normalizer_process.png']
      },
      entry_points={
          'console_scripts': [
              'csv_normalizer = src.__main__:main'
          ]
      },
      install_requires=requires,
      tests_require=['pytest',
                     'pytest-cov'],
      zip_safe=False)
