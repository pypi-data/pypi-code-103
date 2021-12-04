import os
import re
import setuptools

NAME="ndefcdf"
META_PATH = os.path.join(NAME, "__init__.py")
META_FILE = open(META_PATH, "r").read()

def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=NAME,
    version=find_meta("version"),
    license=find_meta("license"),
    author="Petr Kracik",
    author_email="petrkr@petrkr.net",
    description="NDEF Crypto Data Format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/agama-point/"+NAME,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 1 - Planning",
    ],
    install_requires=[
        'ndeflib',
    ],
    python_requires='>=3.4'
)

setuptools.setup(
    name="micropython-"+NAME,
    version=find_meta("version"),
    license=find_meta("license"),
    author="Petr Kracik",
    author_email="petrkr@petrkr.net",
    description="NDEF Crypto Data Format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/agama-point/"+NAME,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 1 - Planning",
    ],
    install_requires=[
        'micropython-ndeflib',
    ],
    python_requires='>=3.4'
)
