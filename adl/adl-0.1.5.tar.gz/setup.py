from setuptools import find_packages, setup

setup(
    name="adl",
    version="0.1.5",
    description="script generator for mumax3 for antidot lattice",
    author="Mathieu Moalic",
    author_email="matmoa@pm.me",
    platforms=["any"],
    license="GPL-3.0",
    url="https://github.com/MathieuMoalic/adl",
    packages=find_packages(),
    install_requires=[i.strip() for i in open("requirements.txt").readlines()],
)
