from setuptools import setup, find_packages

VERSION = '0.1.1'
DESCRIPTION = 'Google Image Scraper'
LONG_DESCRIPTION = 'A package that allows to fetch image urls from google images.'

# Setting up
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
