from setuptools import setup
from setuptools import find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='aicore-nb-tools', 
    version='0.0.2',
    long_description=long_description,
    long_description_content_type='text/markdown',
    description='Create a notebook with questions for AiCore students',
    author='Ivan Ying',
    packages=find_packages(),
    install_requires=['nbformat',
                      'PyYaml',
                      'PyQt5'],
)