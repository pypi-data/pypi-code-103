import setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pytest-testrail-api-client',
    version='0.3.6',
    use_scm_version=False,
    description='TestRail Api Python Client',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Biriukov Maksym',
    author_email='maximbirukov77@gmail.com',
    url="https://github.com/Slamnlc/test-rail-client",
    download_url='https://github.com/Slamnlc/test-rail-client/archive/refs/tags/v0.3.6.tar.gz',
    packages=setuptools.find_packages(exclude=("tests", "dev_tools")),
    install_requires=[
        'requests',
        'pytest',
        'gherkin-official>=4.1.0',
        'pytest-bdd>=3.3.0',
        'typing'
    ],
    entry_points={
        "pytest11": [
            "pytest-testrail-api-client = pytest_testrail_api_client.configure",
        ],
        "testrail_api": [
            "test_rail_client = pytest_testrail_api_client.test_rail"
        ]
    },
)
