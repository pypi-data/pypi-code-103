import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
VERSION = '0.0.1' 
DESCRIPTION = 'Python library for automatic land cover classification of Sentinel 2 satellite images'

setup(
        name="sen2classification", 
        version=VERSION,
        author="Luka Raspovic",
        author_email="<lraspovic993@gmail.com>",
        description=DESCRIPTION,
        long_description=README,
        long_description_content_type="text/markdown",
        url="https://github.com/lraspovic/sen2classification",
        license="MIT",
        packages=find_packages(exclude=("tests",)),
        install_requires=['scikit-learn', 'imbalanced-learn', 'xgboost'],
        keywords=['python', 'sentinel 2', 'machine learning', 'land cover', 'classification', 'automatic', 'satellite', 'image classification'],
        classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        ],
        python_requires='>=3.6'
)