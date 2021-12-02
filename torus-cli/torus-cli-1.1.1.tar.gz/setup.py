import os
import setuptools

rootdir = os.path.abspath(os.path.dirname(__file__))
long_description = open(os.path.join(rootdir, 'README.md')).read()

setuptools.setup(
    name="torus-cli",
    version="1.1.1",
    author="Luca Albinati",
    author_email="luca.albinati@gmail.com",
    description="Command line interface for torus-engine",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/lucaalbinati/torus-cli",
    project_urls={
        "Bug Tracker": "https://github.com/lucaalbinati/torus-cli/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
)