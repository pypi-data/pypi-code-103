import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="calc_demo-mf", #cambiar de nombre por si existe??
    version="0.0.2",
    author="mfermin",
    author_email="email@ib.edu.ar",
    description="Breve descripción",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab/publish",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ),
)
