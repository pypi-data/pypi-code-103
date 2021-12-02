from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='demix_lib',
    version='1.10',
    packages=['demix_lib'],
    url='https://github.com/AlexisMARTICOMTE/demix_lib.git',
    license='mit',
    author='visioterra',
    author_email='info@visioterra.fr',
    description='version 1.10 of the DEMIX library',
    long_description=long_description,
    long_description_content_type="text/markdown",
)
