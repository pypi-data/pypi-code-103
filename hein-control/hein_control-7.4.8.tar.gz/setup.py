import hein_control.version
from setuptools import setup, find_packages

long_description = """
# Hein Control code

This package includes code for automating and scheduling experimental tasks. For detailed information and examples
 please visit the GitLab repository. 
"""

setup(
    name='hein_control',
    version=hein_control.version.__version__,
    packages=find_packages(),
    url='https://gitlab.com/heingroup/hein_control',
    license='MIT',
    author='Lars Yunker // Hein Group',
    author_email='',
    description='Code for automation and scheduling',
    long_description=long_description,
    long_description_content_type='text/markdown',
)
