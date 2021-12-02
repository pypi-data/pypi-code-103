import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="calc_demo_pi", #lib name (debe coincidir con folder_name)
    version="0.0.5",
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
