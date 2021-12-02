from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'Validator Package for Texts and Files'
LONG_DESCRIPTION = 'A package that allows to validate text and file data shared over web.'

# Setting up
setup(
    name="PyWebValidators",
    version=VERSION,
    author="tombstoneGhost (Simardeep Singh)",
    description=DESCRIPTION,
    long_description=long_description,
    packages=find_packages(),
    install_require=['setuptools', 'python-magic'],
    keywords=['python', 'validator', 'security', 'validation'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
