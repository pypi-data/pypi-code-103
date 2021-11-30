import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="drivtime",
    version="0.0.2",
    author="Hugo Carvalho",
    author_email="hugodanielsilvacarvalho.hc@gmail.com",
    description="Driving time and rest periods in the road transport sector framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hugodscarvalho/drivtime",
    packages=setuptools.find_packages(),
    keywords=['python', 'driving time', 'rest periods', 'EU', 'Regulation', 'road transport', 'truck', 'optimization', 'passenger transport', 'transport'  ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)