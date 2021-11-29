# setup.py
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ViNeSeg",
    version="0.0.7",
    author="Nicolas Ruffini, Nico Weber, Saleh Altahini, Anna Wierczeiko, Hendrik Backhaus",
    author_email="nicolas.ruffini@lir-mainz.de",
    description="Image Polygonal Annotation with Python combined with Auto-Segmentation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NiRuff/IntelliPy",
    packages=["vineseg"],
    install_requires = [
        "imgviz>=0.11",
        "matplotlib!=3.3",  # for PyInstaller
        "numpy",
        "Pillow>=2.8",
        "PyYAML",
        "qtpy!=1.11.2",
        "termcolor",
        "monai",
        "pandas",
        "scikit-image>=0.18.1",
        "torchcontrib>=0.0.2",
        "shapely",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
