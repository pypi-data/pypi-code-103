import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="secmind",
    version="1.1",
    author="Godzilla.Y",
    author_email="xphook@gmail.com",
    description="secmind library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/x86arm",
    packages=setuptools.find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    install_requires=[
        "selenium>=3.141.0"
    ],
    python_requires=">=3",
)
