import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mendelai_brat_parser",
    version="0.0.8",
    author="Khaled Essam",
    author_email="khaled.essam@mendel.ai",
    description="BRAT Parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mendelhealth/brat-parser",
    package_dir={"": "brat_parser"},
    packages=[""],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
