import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lockattrs",
    version="0.0.4",
    author="D Reschner",
    author_email="git@simphotonics.com",
    description="Decorator used to lock class attributes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/simphotonics/lockattrs",
    project_urls={
        "Bug Tracker": "https://github.com/simphotonics/lockattrs/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
)
