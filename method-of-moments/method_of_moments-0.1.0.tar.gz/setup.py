"""Module for packaging and distribution Python packages."""


import setuptools

with open("README.md", mode="r", encoding='utf8') as fh:
    long_description = fh.read()

requirements = [
    "math_round_af==1.0.2",
    "numpy==1.21.4",
    "pretty-repr==1.0.1",
    "pylint-af==1.0.1",
    "pytest==6.2.5",
    "scipy==1.7.3",
]

setuptools.setup(
    name="method_of_moments",
    version="0.1.0",
    author="Albert Farkhutdinov",
    author_email="albertfarhutdinov@gmail.com",
    description=(
        "The package that allows you to work with probability distributions "
        "with a specified mean values and variances."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlbertFarkhutdinov/method_of_moments",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
