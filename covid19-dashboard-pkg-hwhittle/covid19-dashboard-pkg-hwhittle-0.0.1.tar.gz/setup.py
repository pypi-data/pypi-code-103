import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="covid19-dashboard-pkg-hwhittle",
    version="0.0.1",
    author="Harry Whittle",
    author_email="harry.whittle@cwgsy.net",
    description="A personalisable UK COVID-19 Dashboard used for demonstration purposes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/itselectroz/covid-dashboard-coursework",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)