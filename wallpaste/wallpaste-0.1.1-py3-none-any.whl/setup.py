from setuptools import setup

# read the contents of your README file
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='wallpaste',
    version='0.1.1',
    packages=[''],
    install_requires=['pillow'],
    url='https://github.com/misobarisic/wallpaste',
    license='MIT',
    author='misobarisic',
    author_email='me@misobarisic.com',
    description='Combine multiple images into one.',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
