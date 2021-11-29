from setuptools import setup, find_packages

VERSION = '0.0.12'
DESCRIPTION = 'Package should be used to square a number.'
# Setting up
setup(
    name="squaremeup",
    version=VERSION,
    author="Ajit",
    author_email="<ajitkulkarni932002@gnamil.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'unitlength', 'length', 'distances', 'diameters', 'meters'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)