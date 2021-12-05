from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read().replace(".. include:: toc.rst\n\n", "")

# The lines below are parsed by `docs/conf.py`.
name = "fountains"
version = "1.2.0"

setup(
    name=name,
    version=version,
    packages=[name,],
    install_requires=["bitlist~=0.6",],
    license="MIT",
    url="https://github.com/reity/fountains",
    author="Andrei Lapets",
    author_email="a@lapets.io",
    description="Python library for generating and concisely specifying"+\
                "reproducible pseudorandom binary data for unit testing.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    test_suite="nose.collector",
    tests_require=["nose"],
)
