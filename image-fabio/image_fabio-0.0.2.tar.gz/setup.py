from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="image_fabio",
    version="0.0.2",
    author="Fabio_Tolentino",
    author_email="fabio.tolentino@uol.com.br",
    description="Pacote para tratar imagens",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FabioTolentino19/image_fabio",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.0',
)