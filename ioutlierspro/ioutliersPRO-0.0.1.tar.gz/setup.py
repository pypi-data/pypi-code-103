import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

SRC = 'src'
setuptools.setup(
    name="ioutliersPRO",
    version="0.0.1",
    author="Dheiver Santos",
    author_email="dheiver.santos@gmail.com",
    description="remove potential outliers or Package to easily detect",
    long_description=long_description,
    package_dir={'': SRC},
    long_description_content_type="text/markdown",
    url="https://.....",
    packages=setuptools.find_packages(SRC),
    include_package_data = True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
          'pandas',
          'rrcf',
          'sklearn',
          'idfops'
      ],
    python_requires='>=3.6',
)
