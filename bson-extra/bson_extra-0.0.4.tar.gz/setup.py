import os

from setuptools import find_packages, setup

about = {}
here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "bson_extra", "__version__.py"), "r") as f:
    exec(f.read(), about)

with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="bson_extra",
    version=about["__version__"],
    description="Provides hooks for supplying extra type handling for bson objects. Primarily to give full timezone support for bson.dumps and bson.loads",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AgileTek Engineering",
    classifiers=[
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3.6",
        "Natural Language :: English",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    install_requires=["pymongo==3.12.2", "pytz"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-mock"],
    extras_require={
        "pre-commit": "pre-commit",
    },
    include_package_data=True,
    zip_safe=False,
)
