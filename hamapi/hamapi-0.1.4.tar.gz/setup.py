import setuptools
import os

__version__ = "0.1.4"

PATH = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(PATH, "README.md"), "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hamapi",
    version=__version__,
    author="Lefteris Chatzipetrou",
    author_email="lefteris@hamsystems.eu",
    description="HAM Systems API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['hamapi'],
    package_dir={"hamapi": "src/hamapi"},
    package_data={"hamapi": ["*.json"]},
    
    install_requires=["requests","brotli"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)