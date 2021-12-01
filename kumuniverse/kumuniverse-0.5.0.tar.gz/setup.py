from setuptools import find_packages, setup


VERSION = "0.5.0"
DESCRIPTION = "Data team shared library for accessing services"

setup(
    name="kumuniverse",
    version=VERSION,
    description=DESCRIPTION,
    author="Renz Abergos",
    author_email="renz@kumu.ph",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "pymongo",
        "pymongo[srv]",
        "pymongo[aws]",
        "requests",
        "UnleashClient",
        "boto3",
        "pandas",
        "sagemaker",
    ],
    extras_require={"databricks": ["pyspark"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
