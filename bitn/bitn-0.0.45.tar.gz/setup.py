import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bitn",
    version="0.0.45",
    author="fu-corp",
    author_email="spam@futzu.com",
    description="a better bitslicer9k",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/futzu/bitn",
    py_modules=["bitn"],
    platforms="all",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    python_requires=">=3.6",
)
