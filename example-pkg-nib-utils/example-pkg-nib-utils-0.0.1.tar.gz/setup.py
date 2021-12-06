import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="example-pkg-nib-utils",
    version="0.0.1",
    author="NIB-Dev-Team",
    author_email="NIB_IT_Dev@nib-bahamas.com",
    description="the site package for nib dev team",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NIB-DEVELOPMENT/NIB_utils.git",
    project_urls={
        "Bug Tracker": "https://github.com/NIB-DEVELOPMENT/NIB_utils.git/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)