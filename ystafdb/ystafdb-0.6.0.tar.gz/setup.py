from setuptools import setup
import os

packages = []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)


# TODO
# Change every instance of `your_library_name` to the name of your library.
# Change `author`
# Change `author_email`
# Change `url`
# Change the PyPI classifiers: https://pypi.org/pypi?%3Aaction=list_classifiers


# Probably should be changed, __init__.py is no longer required for Python 3
for dirpath, dirnames, filenames in os.walk("ystafdb"):
    # Ignore dirnames that start with "."
    if "__init__.py" in filenames:
        pkg = dirpath.replace(os.path.sep, ".")
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, ".")
        packages.append(pkg)


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths


setup(
    name="ystafdb",
    version="0.6.0",
    packages=packages,
    description="CLI tool to parse YSTAFDB and produce ttl/nt/xml.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Emil Riis Hansen",
    author_email="emilrh@cs.aau.dk",
    package_data={"ystafdb": package_files(os.path.join("ystafdb", "data"))},
    # Only if you have non-python data (CSV, etc.). Might need to change the directory name as well.
    # package_data={"your_name_here": package_files(os.path.join("your_library_name", "data"))},
    entry_points={"console_scripts": ["ystafdb-cli = ystafdb.bin.ystafdb:main",]},
    install_requires=["appdirs", "docopt", "rdflib>=6", "pandas", "xlrd", "pyxlsb"],
    url="https://github.com/BONSAMURAIS/ystafdb/",
    classifiers=[
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
)
