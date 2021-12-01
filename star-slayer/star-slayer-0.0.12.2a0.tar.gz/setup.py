from setuptools import setup, find_packages

setup(

    name="star-slayer",

    packages=["starslayer",],

    package_data={

        "starslayer" : ["starslayer/*.txt", "starslayer/levels/*.txt", "starslayer/sprites/player/*.gif"],

        # "starslayer.levels" : ["levels/*.txt"],

        # "starslayer.sprites.player" : ["sprites/player/*.gif"]
    },

    include_package_data=True,

    version="0.0.12.2-alpha",

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

print(f"\n\n\n{find_packages()}\n\n\n")