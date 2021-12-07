from setuptools import setup
import setuptools


requirements = ['pandas>=1.0.0']

setup(
    name='timewarpy',
    version='0.0.2',
    description='Time series processing framework and utilities for deep learning',
    author='Clay Elmore',
    packages=setuptools.find_packages(),
    license='BSD 3-Clause License',
    include_package_data=True,
    install_requires=requirements,
    scripts=[],
    zip_safe=False
)
