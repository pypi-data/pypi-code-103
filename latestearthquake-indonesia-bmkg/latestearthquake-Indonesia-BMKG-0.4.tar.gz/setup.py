"""
https://packaging.python.org/tutorials/packaging-projects/
Markdown Guide : https://www.markdownguide.org/cheat-sheet/
"""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="latestearthquake-Indonesia-BMKG",
    version="0.4",
    author="Christian Yurianja",
    author_email="riautechdev@gmail.com ",
    description="This package will get the latest earthquake from "
                "Indonesia Meteorological, Climatological, and Geophysical Agency (BMKG).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RiauTechDev/latest-eartquake-BMKG",
    project_urls={
        "Medium": "https://riautechdev.medium.com",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable"
    ],
    # package_dir={"": "src"},
    # packages=setuptools.find_packages(where="src"),
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)
