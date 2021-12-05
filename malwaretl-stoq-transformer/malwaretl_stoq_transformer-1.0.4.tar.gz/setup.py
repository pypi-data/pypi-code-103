import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="malwaretl_stoq_transformer",
    version="1.0.4",
    author="Aaron Gee-Clough",
    author_email="aaron@g-clef.net",
    description="Helper class to build Stoq instances for use in MalwareETL pipelines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/g-clef/stoq_transformer",
    project_urls={
            "Bug Tracker": "https://github.com/g-clef/stoq_transformer/issues",
        },
    packages=setuptools.find_packages(where="."),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["stoq-framework", "lief==0.11.5"]
)
