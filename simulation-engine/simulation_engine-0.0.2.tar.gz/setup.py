from setuptools import setup, find_packages

VERSION = '0.0.2' 
DESCRIPTION = 'Engine for simulating relic drops in Warframe.'
LONG_DESCRIPTION = 'Engine for simulating relic drops in Warframe, has several features and is very extensible.'

setup(
        name="simulation_engine", 
        version=VERSION,
        author="Jacob McBride",
        author_email="jake55111@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['relic_engine'],
        keywords=['warframe','relics','simulation'],
        classifiers= [
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
        ]
)