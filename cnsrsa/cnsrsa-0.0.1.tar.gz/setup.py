from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'None of your business'


# Setting up
setup(
    name="cnsrsa",
    version=VERSION,
    author="Anonymous",
    author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",

    packages=find_packages(),
    install_requires=[],
    keywords=['rsa'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)