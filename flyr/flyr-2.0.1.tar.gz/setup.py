import setuptools  # noqa
from distutils.core import setup
from os import path

# Read the contents of README.md
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="flyr",
    packages=["flyr", "flyr.palettes"],
    version="2.0.1",
    license="EUPL v1.2",
    description="Flyr is a library for extracting thermal data from FLIR images written fully in Python, without depending on ExifTool.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Arthur Nieuwland",
    author_email="anieuwland@nimmerfort.eu",
    url="https://bitbucket.org/nimmerwoner/flyr/",
    project_urls={
        "Issues": "https://bitbucket.org/nimmerwoner/flyr/issues?status=new&status=open",
        "Releases": "https://bitbucket.org/nimmerwoner/flyr/downloads/",
        "Author website": "http://nimmerfort.eu",
    },
    download_url="https://bitbucket.org/nimmerwoner/flyr/get/v2.0.1.zip",
    keywords=["flir", "thermography"],
    install_requires=["numpy", "nptyping==0.3.1", "pillow"],
    python_requires=">=3.5",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",  # Specify which pyhton versions that you want to support
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
)
