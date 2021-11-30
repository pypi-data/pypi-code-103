import setuptools

__version__ = "0.1.1"

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

description = "Package to handle complex jsons."

setuptools.setup(
    name="managerjson",
    version=__version__,
    author="Osiel Torres",
    author_email="osieltorresdev@gmail.com",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/osstorres/jsonmanager.git",
    packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Natural Language :: English",
    ],
    python_requires=">=3",
)
