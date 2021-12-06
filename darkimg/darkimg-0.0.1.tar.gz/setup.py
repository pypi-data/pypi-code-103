from setuptools import setup


with open("README.md", "r") as fh:
  long_description = fh.read()

setup(
  name = "darkimg",
  version = "0.0.1",
  description = "Advanced image processer/drawer",
  long_description = long_description,
  long_description_content_type = "text/markdown",
  url = "https://google.com",
  author = "darkdarcool30",
  author_email = "darkdarcool@gmail.com",
  license = "MIT",
  packages=['darkimg'],
  classifiers = [
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
],
  zip_safe=True,
  python_requires = ">=3.6",
)