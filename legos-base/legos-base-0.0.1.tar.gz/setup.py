from setuptools import find_namespace_packages, setup

ldesc = None
with open("README.md", "r") as rme_:
    ldesc = rme_.read()

setup(
    name="legos-base",
    version="0.0.1",
    author="Bhavesh Pandey",
    author_email="bxpandey@pm.me",
    description="A package providing generic base\
 classes and mixins used in the legos api.",
    long_description=ldesc,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_namespace_packages(where="src", include=["legos", "legos.*"]),
    package_dir={"": "src", "legos": "src/legos"},
    install_requires=[],
    extras_require={"dev": ["pytest", "pytest-bdd", "pytest-cov"]},
    python_requires=">=3.8",
)
