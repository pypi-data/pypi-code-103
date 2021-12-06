import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="edapro", 
    version="0.0.2",
    author="Dheiver Santos",
    author_email="dheiver.santos@gmail.com",
    description="EDA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/...",
    download_url = "https://github.com/...",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
