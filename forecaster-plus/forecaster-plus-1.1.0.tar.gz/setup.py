import pathlib
import setuptools


# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setuptools.setup(
    name="forecaster-plus",
    version="1.1.0",
    author="Ben Cassese",
    author_email="b.c.cassese@columbia.edu",
    license="MIT",
    url="https://github.com/ben-cassese/forecaster-plus",
    description="Probabilistically forecast astronomical masses and radii",
    long_description=README,
    long_description_content_type="text/markdown",
    install_requires=["numpy", "scipy", "astropy", "h5py", "setuptools"],
    packages=["forecaster"],
    include_package_data=True
)