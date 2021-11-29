from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    url = "https://github.com/joacomonsalvo/uptwine",
    author = "Joaco Monsalvo",
    author_email = "joacomonsalvo.contact@protonmail.com",
    name = "uptwine",
    version = "0.0.9",
    description = "Auto package uploader to pypi with twine",
    py_modules = ['uptwine'],
    package_dir = {'': 'src'},
    
    long_description = long_description,
    long_description_content_type = "text/markdown",
    
    install_requires = [
        "twine ~= 3.4.2",
        "wheel ~= 0.37.0",
    ],
    
    extra_require = {
        "dev" : [
            "pytest >= 3.7",
        ],
    },
    
    keywords=['python', 'pypi', 'uptwine', 'twine'],
    
    classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    ]
)