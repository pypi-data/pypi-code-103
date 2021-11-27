from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    README = fh.read()

setup(
    name="katsuyou",
    version="0.1.2",
    description="Python japanese toolkit",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/northy/katsuyou",
    project_urls={
        "Bug Tracker": "https://github.com/northy/katsuyou/issues",
    },
    author="Alexsandro Thomas",
    author_email="alexsandrogthomas@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(exclude="tests"),
    python_requires=">=3.6"
)
