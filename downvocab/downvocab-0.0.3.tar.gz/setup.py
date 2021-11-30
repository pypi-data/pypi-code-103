# setup.py

import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="downvocab",
    version="0.0.3",
    description="Download English words",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/takliu/downvocab",
    author="Tak Liu",
    author_email="liutak999@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["downvocab"],
    include_package_data=True,
    install_requires=["gTTS == 2.2.3"],
    entry_points={
        "console_scripts": [
            "downvocab=downvocab.__main__:main",
        ]
    },
)