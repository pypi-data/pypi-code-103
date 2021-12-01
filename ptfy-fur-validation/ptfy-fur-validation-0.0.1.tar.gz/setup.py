import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ptfy-fur-validation",
    version="0.0.1",
    author="Pantherify",
    author_email="pypi@pantherify.com",
    description="A package responsible for securing the communication between systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pantherify/python-utils/tree/main/fur_validation",
    project_urls={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="./src"),
    install_requires=["python-dotenv", "colorama", "coloredlogs"],
    python_requires=">=3.7",
)
