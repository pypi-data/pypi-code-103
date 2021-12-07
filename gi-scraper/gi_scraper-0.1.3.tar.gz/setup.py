from setuptools import setup, find_packages
from pathlib import Path

current_dir = Path(__file__).parent

VERSION = '0.1.3'
DESCRIPTION = 'Google Image Scraper - A package that allows to fetch image urls and download images from google images.'
LONG_DESCRIPTION = (current_dir / "README.md").read_text()

setup(
    name="gi_scraper",
    version=VERSION,
    author="Roy6801",
    author_email="<mondal6801@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['selenium'],
    keywords=['python', 'google images', 'image scraper'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)
