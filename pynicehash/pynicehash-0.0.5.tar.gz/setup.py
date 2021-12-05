import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pynicehash",
    version="0.0.5",
    author="Nicolas Slythe",
    author_email="pynicehash@slythe.net",
    description="Python to interac with Nicehash API v2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nslythe/pynicehash",
    project_urls={
        "Bug Tracker": "https://github.com/nslythe/pynicehash/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=["requests"]
)