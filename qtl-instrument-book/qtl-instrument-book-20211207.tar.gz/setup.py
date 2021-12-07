from setuptools import setup, find_packages

setup(
    name='qtl-instrument-book',
    version='20211207',
    description='Quantalon Instrument Book',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'toml',
    ]
)
