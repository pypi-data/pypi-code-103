from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.7'
DESCRIPTION = 'Simplyfing the process of creating cybersecurity tools'
LONG_DESCRIPTION = 'A package that allows to build hacking tools without any efforts. Hence it simplifies the process of security testing in an enviornment where there are no readymade tools available.'

# Setting up
setup(
    name="simplyhack",
    version=VERSION,
    author="Abhishek Uday Dangat",
    author_email="abshdangat@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    py_modules=["simplyhack"],
    package_dir={'': 'src'},
    packages=find_packages(),
    install_requires=['scapy', 'scapy_http', 'colorama', 'pikepdf', 'zipfile', 'rarfile'],
    keywords=['python', 'hacking', 'cybersecurity', 'hacking tools', 'security testing', 'hacker'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
