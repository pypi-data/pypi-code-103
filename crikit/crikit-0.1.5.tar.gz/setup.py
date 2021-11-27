from setuptools import setup, find_packages
from itertools import chain
import os
import pathlib

python_requires = ">=3.7"
install_requires = [
    "dolfin-adjoint >= 2019.1.1",
    "numpy",
    "autograd",
    "petsc4py>=3.11.0",
    "jax",
    "jaxlib",
]
extras_requires = {
    "test": ["pytest>=3.10", "pytest-rerunfailures", "flake8", "coverage"],
    "visualization": ["matplotlib"],
    "flax": ["flax"],
    "tensorflow": ["tensorflow>=2.0"],
    "doc": [
        "sphinx",
        "myst-nb",
        "sphinxcontrib-bibtex",
        "sphinxcontrib-katex",
        "pydata-sphinx-theme",
        "linkify-it-py",
    ],
    "dev": ["black", "pre-commit", "build"],
}

extras_requires["all"] = list(chain(*extras_requires.values()))

dependency_links = [
    "git+https://github.com/dolfin-adjoint/pyadjoint.git@master",
]

classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

url = "https://gitlab.com/crikit/crikit"

project_urls = {
    "Bug Tracker": "https://gitlab.com/crikit/crikit/issues",
    "Documentation": "https://crikit.science/documentation",
}

version_file = os.path.join(os.path.dirname(__file__), "crikit/_version.py")
with open(version_file, "r") as f:
    version = f.read().split("=", 1)[1].strip(" \n\"'")


HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="crikit",
    version=version,
    description="Constitutive Relation Inference Toolkit",
    long_description=README,
    long_description_content_type="text/markdown",
    author="CRIKit Team",
    classifiers=classifiers,
    url=url,
    project_urls=project_urls,
    packages=find_packages(exclude=["examples", "tests"]),
    python_requires=python_requires,
    install_requires=install_requires,
    dependency_links=dependency_links,
    extras_require=extras_requires,
)
