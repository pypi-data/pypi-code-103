from setuptools import setup, find_packages


def get_long_description():
    with open("README.md", encoding="utf8") as f:
        return f.read()


setup(
    name="pointless-db",
    version="0.0.1",
    description="Pointless database plugin for sqlDash",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="WardPearce",
    author_email="wardpearce@pm.me",
    license="GPL-3.0",
    py_modules=["plugin"],
    packages=find_packages(),
    python_requires=">=3.6",
    include_package_data=True,
    zip_safe=False
)
