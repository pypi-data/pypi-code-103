import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "alpdataneuron",
    version = "0.2.9",
    author = "Nishant Chhetri",
    author_email = "nishant.chhetri@precily.com",
    description = "alpdataneuron package",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "http://20.43.152.82:4000",
    include_package_data = True,
    packages = setuptools.find_packages(),
    install_requires = [
        'requests'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires = '>=3.6',
)
