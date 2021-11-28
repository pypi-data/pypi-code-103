from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name = 'aac_distributions',
      version = '0.6',
      packages = ['aac_distributions'],
      author = 'Alberto Armero',
      author_email = 'alberto.armero86@gmail.com',
      description = 'Gaussian and Binomial distributions',
      long_description = long_description,
      long_description_content_type = "text/markdown",
      classifiers =[
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
      ],
      zip_safe = False)
