from setuptools import setup, find_packages

from credit_card_clients_model.config import config


setup(
    name="credit_card_clients_model",
    packages=find_packages(),
    version=config.VERSION,
    author="Matthew Aguerreberry",
    description="credit card clients model",
    python_requires=">=3.7",
)
