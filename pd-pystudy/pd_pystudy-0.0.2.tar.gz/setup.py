import setuptools
#©copyrightPVGOBSERVER
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pd_pystudy",
    version="0.0.2",
    author="pvgobserver",
    author_email="variflight@feiyou.chat",
    description="a easy package of Shanghai student for easy study",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/pypa/sampleproject",
    # project_urls={
        # "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    # },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # package_dir={"": "src"},
    packages=setuptools.find_packages(),
    python_requires=">=3.5",
)