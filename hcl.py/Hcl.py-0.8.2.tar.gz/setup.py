from setuptools import setup, find_packages
from hcl.__init__ import __version__, __title__
with open("README.md", "r") as readme: long_description = readme.read()


setup(
    name=__title__,
    version=__version__,
    url="https://github.com/Oustex/hcl.py",
    download_url="https://github.com/Oustex/hcl.py/tarball/master",
    license="Apache V2",
    author="Oustex",
    author_email="oustexp@gmail.com",
    description="An api including Amino web and app websocket",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=[
        "aminoapps",
        "hcl-py",
        "Hydrochloric.py",
        "Hydrochloric-py",
        "Hydrochloric",
        "amino",
        "amino-bot",
        "narvii",
        "api",
        "slimakoi",
        "kapidev",
        "syscall",
        "oustex",
        "AminoBot",
        "botamino",
        "aminobot",
    ],
    install_requires=[
        "websocket-client",
        "wheel",
        "requests",
        "progress",
        "json_minify",
        "aiohttp",
        "typing",
        "Amino-Socket"
    ],
    setup_requires=["wheel"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        'Source': 'https://github.com/Oustex/Hcl.py',
    },
    packages=find_packages()
)
