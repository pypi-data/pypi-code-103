from setuptools import setup, find_packages

project_description = ''

with open("README.md", mode='r') as readme:

    project_description = readme.read()

setup(

    name="star-slayer",

    packages=find_packages(),

    package_data={

        "starslayer" : ["*.txt",
                        "levels/*.txt",
                        "sprites/player/*.gif"]
    },

    version="0.0.14-alpha",

    url="https://github.com/NLGS2907/star-slayer",

    author="NLGS",

    author_email="flighterman@fi.uba.ar",

    license="MIT",

    description="Little game made with Gamelib",

    long_description=project_description,

    long_description_content_type="text/markdown",

    classifiers=[

        "Development Status :: 3 - Alpha",

        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 3.10"
    ]
)