# 
#   RawIO
#   Copyright (c) 2021 Yusuf Olokoba.
#

from setuptools import find_packages, setup

# Get readme
with open("README.md", "r") as readme:
    long_description = readme.read()

# Get version
with open("rawio/version.py") as version_source:
    gvars = {}
    exec(version_source.read(), gvars)
    version = gvars["__version__"]

# Setup
setup(
    name="rawio",
    version=version,
    author="Yusuf Olokoba",
    author_email="hi@hdk.ai",
    description="RAW and raster image IO.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
	python_requires=">=3.6",
    install_requires=[
        "exifread",
        "lensfunpy",
        "imagehash",
        "imageio",
        "opencv-python-headless",
        "piexif",
        "pillow",
        "python-dateutil",
        "rawpy",
        "scikit-learn",
        "scipy",
        "torch",
        "torchvision"
    ],
    url="https://github.com/hdkai/Raw-IO",
    packages=find_packages(
        include=["rawio", "rawio.*"],
        exclude=["test", "playground"]
    ),
    package_data={ "rawio.raw": ["data/*.tif"] },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Software Development :: Libraries",
    ],
    project_urls={
        "Documentation": "https://docs.hdk.ai/rawio",
        "Source": "https://github.com/hdkai/Raw-IO"
    },
)
