from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.2'
DESCRIPTION = 'An Intelligent Bot Framework to build simple yet powerful Assistance Bots.'
LONG_DESCRIPTION = 'An Fully Customizable Intelligent Bot Framework to build simple yet powerful Assistance Bots, allowing to do Web Searches and process Natural and Boolean Responses.'

# Setting up
setup(
    name="microbotpkg",
    version=VERSION,
    author="Juan Carlos Juárez",
    author_email="<jc.juarezgarcia@outlook.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['lxml', 'googlesearch-python', 'animation', 'pyttsx3', 'beautifulsoup4'],
    keywords=['python', 'Bot', 'Framework'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)