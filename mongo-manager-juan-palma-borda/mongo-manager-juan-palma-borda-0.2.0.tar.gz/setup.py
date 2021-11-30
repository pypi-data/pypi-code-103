import setuptools
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mongo-manager-juan-palma-borda",
    version="0.2.0",
    author='Juan Palma Borda',
    author_email='juanpalmaborda@hotmail.com',
    description='Libreria para manejar objetos almacenados en MongoDB, '
                'usando la referencia de los CRUDRepository de SpringBoot',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url = "https://github.com/muerterauda/mongo_manager",
    project_urls={
        "Bug Tracker": "https://github.com/muerterauda/mongo_manager/issues",
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
