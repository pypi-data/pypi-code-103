import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
    
def _requires_from_file(filename):
    return open(filename, encoding="utf8").read().splitlines()

setuptools.setup(
    name="cb0tcc.py",
    version="0.0.7",
    author="DMS",
    author_email="masato190411@gmail.com",
    description="This can create shorturl.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tuna2134/cb0t.py",
    install_requires=_requires_from_file('rqs.txt'),
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
