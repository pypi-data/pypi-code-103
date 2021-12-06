from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="LVREML",
    version="0.1.0",
    author="Muhammad Ammar Malik",
    author_email="muhammad.malik@uib.no",
    description="LVREML - Restricted maximum-likelihood solution for linear mixed models with known and latent variance components LVREML computes the restricted maximum-likelihood solution for linear mixed models with known and latent variance components",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AmmarMalik93/LVREML-Python",
 #   project_urls={
 #       "Bug Tracker": "",
 #   },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=['lvreml']
)
