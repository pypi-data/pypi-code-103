import os

import setuptools

from version import __version__

CURRENT_FILEPATH = os.path.abspath(os.path.dirname(__file__))
VERSION_FILENAME = 'version.py'


setuptools.setup(
    name='bbc-dslib',
    version=__version__,
    author='Raphaël Berly',
    author_email='raphael.berly@blablacar.com',
    description='A lib for the Data Science team at Blablacar',
    license='closed',
    url="https://github.com/blablacar/data-dslib",
    packages=setuptools.find_packages(),
    python_requires='>=3.7.9',
    install_requires=['humanfriendly', 'pyyaml', 'jinja2'],
    extras_require={
        'database': ['sqlalchemy', 'psycopg2-binary', 'PyMySQL', 'pandas'],
        'facebook': ['fbprophet'],
        'google': [
            'google-cloud-bigquery==2.30.1',
            'google-cloud-bigquery-storage==2.10.1',
            'google-cloud-storage==1.43.0',
            'google-api-python-client==2.31.0',
            'oauth2client==4.1.3',
            'pandas==1.3.4',
            'pandas-gbq==0.16.0',
            'tqdm==4.62.3',
            'gspread==4.0.1',
            'gspread-dataframe==3.2.1'
        ],
        'science': [
            'scikit-learn==1.0.1',
            'numpy==1.21.4',
            'matplotlib==3.5.0',
            'dill==0.3.4',
            'pandas==1.3.4'
        ],
        'testing': ['pytest', 'pytest-cov', 'coverage', 'mock', 'testfixtures'],
    }
)
