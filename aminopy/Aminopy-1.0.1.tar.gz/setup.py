from setuptools import setup, find_packages

with open("README.md", "r") as stream:
    long_description = stream.read()

setup(
    name="Aminopy",
    version="1.0.1",
    url="https://github.com/Oustex/Aminopy",
    download_url="https://github.com/Oustex/Aminopy/tarball/master",
    license="Apache V2",
    author="Oustex",
    author_email="oustexp@gmail.com",
    description="A library to create Amino bots.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=[
        "aminoapps",
        "amino-py",
        "amino",
        "amino-bot",
        "narvii",
        "api",
        "oustex",
        "slimakoi",
        "aminopy",
        "official"
    ],
    install_requires=[
        "setuptools",
        "requests",
        "six",
        "websocket-client==0.57.0",
        "json_minify"
    ],
    setup_requires=["wheel"],
    packages=find_packages()
)
