import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="plagy-mnk",
    version="0.1",
    author="Manish Pandey",
    author_email="mnkp.qc@gmail.com",
    description="A Simple Plagiarism Checker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mnk-q/plagy",
    install_requires=['scikit-learn'],
    project_urls={
        "Bug Tracker": "https://github.com/mnk-q/plagy/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)