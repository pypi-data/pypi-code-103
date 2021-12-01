from setuptools import setup, find_packages

setup(
    name="spreg-satosa-sync",
    python_requires=">=3.6",
    url="https://github.com/CESNET/spreg-satosa-sync.git",
    description="Script to read clients attributes from Perun RPC and write them to mongoDB for SATOSA",
    packages=find_packages(),
    install_requires=[
        "setuptools",
        "pycryptodome==3.11.0",
        "pymongo==3.12.1",
        "requests==2.26.0",
        "PyYAML==6.0",
    ],
)
