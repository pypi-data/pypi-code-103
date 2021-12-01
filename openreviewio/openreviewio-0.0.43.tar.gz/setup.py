import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="openreviewio",
    version="0.0.43",
    author="Félix David",
    author_email="felixg.david@gmail.com",
    description="OpenReviewIO Python API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/openreviewio/openreviewio_py",
    packages=setuptools.find_packages(),
    py_modules=["openreviewio"],
    license="License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["toml", "lxml"],
    include_package_data=True,
)
