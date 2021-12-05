import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="countybot_us",
    version="0.0.3",
    author="Adrià Mercader",
    author_email="amercadero@gmail.com",
    description="A Twitter bot built with munibot that tweets imagery of US Counties and equivalent units",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amercader/countybot_us",
    packages=setuptools.find_packages(),
    install_requires=[
        "munibot",
        "requests",
        "gdal==3.0.4"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "munibot_profiles": [
            "us=countybot_us.profile:CountyBotUS",
        ],
    },
)
