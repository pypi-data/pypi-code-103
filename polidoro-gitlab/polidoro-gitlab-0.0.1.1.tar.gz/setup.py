"""
Setup to create the package
"""
import polidoro_gitlab
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='polidoro-gitlab',
    version=polidoro_gitlab.VERSION,
    description='Polidoro GitLab.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/heitorpolidoro/polidoro-gitlab',
    author='Heitor Polidoro',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
    install_requires=['python-gitlab'],
    include_package_data=True
)
