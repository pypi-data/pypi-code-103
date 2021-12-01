import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="totptray",
    version="1.1.0",
    description="A simple tray icon tool with a TOTP implementation.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/McCzarny/totptray",
    author="Maciej Czarnecki",
    author_email="mcczarny@gmail.com",
    license="The Unlicense",
    classifiers=[
        "License :: OSI Approved :: The Unlicense (Unlicense)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["totptray"],
    include_package_data=True,
    install_requires=["pyperclip", "pystray", "pyotp"],
    entry_points={
        "console_scripts": [
            "totptray=totptray.__main__:main",
        ]
    },
)
