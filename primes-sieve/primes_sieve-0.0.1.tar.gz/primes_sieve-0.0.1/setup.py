from setuptools import setup
from setuptools.config import read_configuration
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

conf_dict = read_configuration('setup.cfg')

setup()