import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cbmi_utils",
    version="0.3.10",
    author="Patrick Baumann",
    author_email="Patrick.Baumann@htw-berlin.de",
    description="Utility package for common features at CBMI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.tools.f4.htw-berlin.de/baumapa/cbmi_utils",
    packages=setuptools.find_packages(
        exclude=(
            "tests",
        )
    ),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "h5py>=3.0.0",
        "numpy>=1.17.0",
        "seaborn>0.11.0",
        "scikit-learn>=1.0.0",
        "torch>=1.7.1",
        "torchinfo==1.5.1",
        "torchmetrics>=0.5.0",
        "torchvision>=0.8.2",
        "umap-learn>=0.5.0"
    ],
)
