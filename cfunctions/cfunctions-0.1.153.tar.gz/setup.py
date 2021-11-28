import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cfunctions",
    "version": "0.1.153",
    "description": "cfunctions",
    "license": "Apache-2.0",
    "url": "https://github.com/eladb/cfunctions.git",
    "long_description_content_type": "text/markdown",
    "author": "Elad Ben-Israel<benisrae@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/eladb/cfunctions.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cfunctions",
        "cfunctions._jsii"
    ],
    "package_data": {
        "cfunctions._jsii": [
            "cfunctions@0.1.153.jsii.tgz"
        ],
        "cfunctions": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii>=1.46.0, <2.0.0",
        "publication>=0.0.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
