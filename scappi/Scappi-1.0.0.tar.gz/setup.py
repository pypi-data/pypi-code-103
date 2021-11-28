import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Scappi",
    url="https://github.com/kruffer/Scappi",
    version="1.0.0",
    author="MrFluid",
    license="MIT",
    description="Python to Scratch API Bridge",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["websocket-client","ScratchEncoder", "requests"]
)