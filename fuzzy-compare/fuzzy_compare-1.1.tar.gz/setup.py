from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(name='fuzzy_compare',
    version='1.1',
    author='Abdullah Saquib',
    author_email='abdullahsaquib@gmail.com',
    packages=find_packages(),
    description='The package includes a algorithm to calculate similarity between two strings',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AbdullahSaquib/fuzzy_compare",
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    keywords=['python', 'str', 'fuzzy', 'compare', 'strings', 'similarity'])