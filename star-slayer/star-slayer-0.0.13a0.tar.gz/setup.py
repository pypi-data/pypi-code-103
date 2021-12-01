from setuptools import setup, find_packages

setup(

    name="star-slayer",

    packages=["starslayer",],

    package_data={

        "starslayer" : ["*.txt", "levels/*.txt", "sprites/player/*.gif"]
    },

    version="0.0.13-alpha",

    url="https://github.com/NLGS2907/star-slayer",

    author="NLGS",

    author_email="flighterman@fi.uba.ar",

    license="MIT",

    description="Little game made with Gamelib",

    classifiers=[

        "Development Status :: 3 - Alpha",

        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 3.10"
    ]
)