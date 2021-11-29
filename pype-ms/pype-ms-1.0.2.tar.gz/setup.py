from setuptools import setup, find_packages

setup(
    author="Mathias Schreiner",
    author_email="matschreiner@gmail.com",
    url="https://gitlab.com/matschreiner/pype",
    download_url="https://gitlab.com/matschreiner/pype/-/archive/v1.0.2/pype-v1.0.2.tar.gz",
    name="pype-ms",
    version="1.0.2",
    packages=find_packages(),
    install_requires=[
        "pyyaml==5.4",
        "pytest",
        "Click",
    ],
    entry_points={
        "console_scripts": [
            "pype = pype.cli:cli",
        ],
    },
)
