import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rvmendillo-image-to-ascii",
    version="1.1.0",
    author="Rey Victor Mendillo",
    author_email="admin@rvmendillo.com",
    description="Generates and saves ASCII texts and colored images from pixels of a JPEG file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rvmendillo/image-to-ascii",
    project_urls={
        "Bug Tracker": "https://github.com/rvmendillo/image-to-ascii/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Text Processing"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
