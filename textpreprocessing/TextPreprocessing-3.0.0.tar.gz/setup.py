from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname("./"))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '3.0.0'
DESCRIPTION = 'NLP Text perprocessor'
LONG_DESCRIPTION = 'The package is intelligent enought to cleanup all the stopwords, cleanup all the unwanted text utterances and the less frequent word lists, etc'

# Setting up
setup(
    name="TextPreprocessing",
    version=VERSION,
    author="Arun Kesavan",
    author_email="<arunkottilukkal@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['textblob', 'spacy', 'bs4'],
    keywords=['python', 'text preprocessing', 'nlp']
)