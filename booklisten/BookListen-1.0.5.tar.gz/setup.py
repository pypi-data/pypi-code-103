import setuptools
from booklisten import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="BookListen",
    version=__version__,
    author="Israel Waldner",
    author_email="imky171@gmail.com",
    description="A command line tool to convert text files to audiobooks",
    url="https://github.com/mordy-python/booklisten",
    long_description=long_description,
    long_description_content_type="text/markdown",
    platforms="any",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["click", "gtts"],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    entry_points={"console_scripts": ["booklisten=booklisten.__main__:cli"]},
)
