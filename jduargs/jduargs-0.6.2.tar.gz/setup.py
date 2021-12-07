import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="jduargs",
    version="0.6.2",
    scripts=["bin/jduargs"],
    author="Jean Demeusy",
    author_email="dev.jdu@gmail.com",
    description="A simple command line argument parser package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeandemeusy/jdu_args",
    packages=["jduargs"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["pyyaml"],
)
