import setuptools

with open("requirements.txt", "r") as file_:
    requirements = file_.readlines()

with open("README.md", "r") as file_:
    readme = file_.read()

setuptools.setup(
    name="minici",
    version="1.0.0",
    author="Anthony Zimmermann",
    author_email="anthony.zimmermann@protonmail.com",
    license="BSD-3-Clause",
    description="A tool that executes commands whenever selected files change.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/AnthonyZimmermann/minici",
    packages=setuptools.find_packages(),
    scripts=["minici/minici"],
    install_requires=requirements,
    include_package_data=False
)
