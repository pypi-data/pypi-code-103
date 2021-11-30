import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requirements = ["requests>=2.21.0", ]

setuptools.setup(
    name="veriftools",
    version="1.0.3",
    author="Martin",
    author_email="veriftools@gmail.com",
    description="Package for generating images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com",
    project_urls={
        "Bug Tracker": "https://github.com",
    },
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
)
