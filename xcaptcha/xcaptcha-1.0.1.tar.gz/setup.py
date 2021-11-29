from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    requirements = f.read().split("\n")

setup(
    name="xcaptcha",
    version="v1.0.1",
    author="Luca Chang",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=requirements,
)
