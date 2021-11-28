from setuptools import setup, find_packages

VERSION = '0.0.8'
DESCRIPTION = 'A Python 3.x package to implement Matrices and almost all its Properties'

file = open("readme.md", encoding='utf-8')
LONG_DESCRIPTION = file.read()

# Setting up
setup(
    name="pymatrices",
    version=VERSION,
    author="Programmin-in-Python (MK)",
    author_email="<kalanithi6014@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    python_requires=">=3",
    project_urls={"HomePage":"https://github.com/Programmin-in-Python/PyMatrices"},
    keywords=['python3', 'matrices', 'eigenvalues', 'Mathematics', 'mathematics', 'maths', 'pymatrices', 'PyMatrices', 'eigenvectors', '2D matrix'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics"
    ]
)