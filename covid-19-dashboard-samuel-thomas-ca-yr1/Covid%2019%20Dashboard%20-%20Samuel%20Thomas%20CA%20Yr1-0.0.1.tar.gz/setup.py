import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Covid 19 Dashboard - Samuel Thomas CA Yr1",
    version="0.0.1",
    author="Samuel Thomas",
    author_email="scct201@exeter.ac.uk",
    description="A module to create and communicate with a covid 19 flask dashboard",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/Covid 19 Dashboard - Samuel Thomas CA Yr1/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">-3.6"
)
