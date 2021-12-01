from setuptools import find_packages, setup
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="harrix-pyssg",
    version="0.5",
    description="Static site generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Harrix/harrix-pylib",
    author="Anton Sergienko",
    author_email="anton.b.sergienko@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["markdown", "harrix-pylib"],
    zip_safe=False
)
