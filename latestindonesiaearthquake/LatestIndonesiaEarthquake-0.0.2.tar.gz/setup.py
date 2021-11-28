import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="LatestIndonesiaEarthquake",
    version="0.0.2",
    author="Tedy Maradho Pasa",
    author_email="maradho@gmail.com",
    description="This package will produce the latest Indonesia earthquake",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kodinge/latest-indonesia-earthquake",
    project_urls={
        "Youtube": "https://www.youtube.com/channel/UCaWfnzdzI9T4nGRq1TR_fMg",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    # package_dir={"": "src"},
    # packages=setuptools.find_packages(where="src"),
    packages=setuptools.find_packages(),
    python_requires=">=3.6",)
