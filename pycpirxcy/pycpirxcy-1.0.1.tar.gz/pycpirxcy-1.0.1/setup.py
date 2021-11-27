import setuptools

name = 'pycpirxcy'


setuptools.setup(
    name=name,
    version="1.0.0",
    author="Pirxcy",
    description="24/7 Fortnite Lobbybot With Admin Controls",
    long_description="24/7 Fortnite Lobbybot With Admin Controls",
    long_description_content_type="text/markdown",
    url="https://github.com/KiyatoFN/KiyatoFNBot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'sanic==21.6.2',
        'fortnitepy',
        'aiohttp',
        'crayons',
        'psutil',
        'PirxcyPinger'
    ],
)
