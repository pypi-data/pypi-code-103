import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="baseutils_phornee",
    version="0.0.14",
    author="Ismael Raya",
    author_email="phornee@gmail.com",
    description="Utility modules for Class management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Phornee/baseutils_phornee",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'PyYAML>=5.3.1'
    ],
    python_requires='>=3.6',
)