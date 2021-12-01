import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="selenium_extension",
    version="1.8.0",
    description="Provides additional methods for selenium automation",
    long_description=README,
    long_description_content_type="text/markdown",
    author="CyberSecure",
    author_email="krishj8000@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["selenium_extension"],
    include_package_data=True,
    install_requires=["selenium", "webdriver_manager"],

)