from setuptools import setup, find_packages

VERSION = '0.0.2'
DESCRIPTION = 'My First Python Package TeeHee'
LONG_DESCRIPTION = 'My First Python Package TeeHeeHeeeeee'

# The important stuff
setup(
    # The name must match the folder name 'verysimplemodule'
    name='verysimplemodulebjk116',
    version=VERSION,
    author='Brian Karab',
    author_email='karabinchak.brian@gmail.com',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    # Here is where bs4 would go for webscraping
    keywords=['python', 'first package'],
    classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
    ]
)