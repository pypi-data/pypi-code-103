import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="text-analyzer-DENYS-IVANENKO",
    version="0.0.1",
    author="Denys Ivanenko",
    author_email="denys_ivanenko@epam.com",
    description="Text Analyzer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.epam.com/denys_ivanenko/advancedpython1hw",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
)