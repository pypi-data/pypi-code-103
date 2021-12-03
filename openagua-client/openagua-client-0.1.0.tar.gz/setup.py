import setuptools

VERSION = '0.1.0'

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="openagua-client",
    version=VERSION,
    license="MIT",
    author="David Rheinheimer",
    author_email="david.rheinheimer@tec.mx",
    description="A very thin wrapper around the OpenAgua web API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/openagua/openagua-client",
    packages=setuptools.find_packages(),
    install_requires=["requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
