from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.2.6'
DESCRIPTION = 'subsidiary-parent names matching score with the given relationship'
LONG_DESCRIPTION = 'Returns a score of 2 companies to be either parent or subsidiary, with the relationship corresponding'

# Setting up
setup(
    name="subsidiary_parent_score",
    version="0.2.6",
    author="camillebrl (Camille Barboule)",
    author_email="camille.barboule@gmail.com",
    description="Returns a score of 2 companies to be subsidiaries or parent",
    long_description_content_type="text/markdown",
    packages= find_packages(), 
    package_dir={'subsidiary_parent_score': 'subsidiary_parent_score'},
    package_data={'': ['data/*.csv', '*.csv']},
    install_requires=['company_name_matching2==0.0.5'],
    keywords=['python', 'subsidiary', 'matching', 'parent', 'country', 'name'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
