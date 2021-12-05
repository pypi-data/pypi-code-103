import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = fh.read().splitlines()

setuptools.setup(
    name="batchify",
    version="0.0.2",
    author="Michael Arcidiacono",
    author_email="",
    description="batchify anything",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mixarcid/batchify",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=requirements
)
