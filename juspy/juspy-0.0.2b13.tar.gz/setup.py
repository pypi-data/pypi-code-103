import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="juspy",
    version="0.0.2b13",
    author="Jaspreet Singh",
    author_email="contact@juspreet51.in",
    description="An EDA and modellling assist library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/juspreet51/juspy",
    download_url="https://github.com/juspreet51/juspy",
    project_urls={
        "Bug Tracker": "https://github.com/juspreet51/juspy",
        "Documentation":  "https://github.com/juspreet51/juspy",
        "Source Code": "https://github.com/juspreet51/juspy",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    install_requires=[
        # seaborn 0.11.2 carries 'numpy>=1.16', 'pandas>=0.24', 'matplotlib>=3.0'
        "seaborn>=0.11.2"
    ],
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
