from setuptools import setup, find_packages

VERSION = '0.0.2' 
DESCRIPTION = 'Engine for generating dictionaries of relics and prime sets.'
LONG_DESCRIPTION = 'Engine for generating dictionaries of relics and prime sets using Digital Extreme\'s PC drops website and warframe.market price data.'

setup(
        name="relic_engine", 
        version=VERSION,
        author="Jacob McBride",
        author_email="jake55111@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['lxml'],
        package_data={'': ['relic_list.json','relic_data.json','set_data.json','wfcd_api.json']},
        include_package_data=True,
        keywords=['warframe','relics','prime'],
        classifiers= [
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
        ]
)