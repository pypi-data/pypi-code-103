from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='pygenricher',  # Required
    version='0.0.25',
    url='https://github.com/bammor/pygenricher',
    author='Bashar Morouj',
    author_email='bashar.morouj@gmail.com',
    package_data={"pygenricher": ["Data/*"]},
    packages=find_packages(),
    python_requires='>=3.6, <4',
    install_requires=['numpy', 'gseapy', 'pandas', 'plotly', 'kaleido'],
    entry_points={"console_scripts": ["pygenricher=pygenricher.GeneEnrichment:main"]}
)
