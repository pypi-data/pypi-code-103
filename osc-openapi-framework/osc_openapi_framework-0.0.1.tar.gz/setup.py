import setuptools
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def get_version():
    root_path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(root_path, 'VERSION'), 'r') as fd:
        return fd.read().strip()

setuptools.setup(
    name="osc_openapi_framework",
    version=get_version(),
    author="Outscal SAS",
    author_email="opensource@outscale.com",
    description="Framework to build/parse OpenAPI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/outscale/osc_openapi_framework",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    license="BSD",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=[
        "prance",
        "openapi-spec-validator"
    ]
)