from setuptools import setup, find_packages

setup(
    name="spreg-satosa-sync",
    url="https://github.com/CESNET/spreg-satosa-sync.git",
    description="Script to read clients attributes from Perun RPC and write them to mongoDB for SATOSA",
    packages=find_packages(),
    install_requires=["setuptools"],
)
