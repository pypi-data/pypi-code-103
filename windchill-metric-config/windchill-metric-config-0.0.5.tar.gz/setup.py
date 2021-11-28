from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="windchill-metric-config",
    version="0.0.5",
    author="Matthias Hippen",
    author_email="hippen@gmx.ch",
    description="Config reader for mimamorisan",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/cax-team/mimamori-san",
    project_urls={
        "Bug Tracker": "https://gitlab.com/cax-team/mimamori-san",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        'ruamel.yaml',
        'prometheus-client'
    ]
)
