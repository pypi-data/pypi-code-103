from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setup(
    name="matrixsolverv1",
    version="0.0.1",
    author="Lukas Harris",
    author_email="186.lukas@gmail.com",
    description="A matrix calculator.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/matsolver",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)