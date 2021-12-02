"""
    Set up the sdc_helpers package
"""
from setuptools import setup


def get_required(file_name):
    """
        Get Required Filename during setup
    """
    with open(file_name):
        return file_name.read().splitlines()


setup(
    name='sdc-helpers',
    packages=[
        'sdc_helpers',
        'sdc_helpers.models',
        'sdc_helpers.airflow_helpers',
        'sdc_helpers.yaml_helpers'
    ],
    install_requires=['sqlalchemy', 'pymysql', 'redis', 'boto3', 'requests'],
    extras_require={
        'airflow': ['dag_factory'],
    },
    description='Global SDC Helpers package',
    version='1.9.0',
    url='https://github.com/RingierIMU/sdc-global-all-helpers',
    author='Ringier South Africa',
    author_email='tools@ringier.co.za',
    keywords=['pip', 'helpers'],
    download_url='https://github.com/RingierIMU/sdc-global-all-helpers/archive/v1.9.0.zip'
)
