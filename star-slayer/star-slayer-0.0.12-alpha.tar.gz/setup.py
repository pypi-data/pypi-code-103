from distutils.core import setup

setup(

    name="star-slayer",

    packages=["starslayer",],

    package_data={

        "starslayer" : ["*.txt"],

        "starslayer.levels" : ["*.txt"],

        "starslayer.sprites.player" : ["*.gif"]
    },

    include_package_data=True,

    version="0.0.12-alpha",

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