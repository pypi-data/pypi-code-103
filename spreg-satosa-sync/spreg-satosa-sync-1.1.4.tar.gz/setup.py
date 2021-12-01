from setuptools import setup, find_packages

setup(
    name="spreg-satosa-sync",
    python_requires=">=3.6",
    url="https://github.com/CESNET/spreg-satosa-sync.git",
    description="Script to read clients attributes from Perun RPC and write them to mongoDB for SATOSA",
    packages=find_packages(),
    install_requires=[
        "setuptools",
        "pycryptodomex>=3.11.0,<4",
        "pymongo>=3.12.1,<4",
        "requests>=2.26.0,<3",
        "PyYAML>=6.0,<7",
    ],
)
