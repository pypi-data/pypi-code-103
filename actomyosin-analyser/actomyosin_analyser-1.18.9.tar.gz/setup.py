"""
USAGE: 
   o install in develop mode: navigate to the folder containing this file,
                              and type 'pip install --user -e .'.
                              (omit '--user' if you want to install for
                               all users or in virtualenv/conda env)
"""
from setuptools import setup, find_packages

setup(name='actomyosin_analyser',
      version='1.18.9',
      description='Analysis tools for actomyosin data',
      url='',
      author='Ilyas Kuhlemann',
      author_email='ilyasp.ku@gmail.com',
      license='GPLv3',
      packages=find_packages('.'),
      entry_points={
          "console_scripts": [
          ],
          "gui_scripts": [
          ]
      },
      install_requires=['numpy',
                        "matplotlib",
                        "h5py",
                        "numba",
                        "pandas",
                        "scipy",
                        "importlib-metadata; python_version < '3.8'"],
      zip_safe=False)
