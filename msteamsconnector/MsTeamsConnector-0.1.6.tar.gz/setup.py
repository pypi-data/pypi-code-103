from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='MsTeamsConnector',
    version='0.1.6',
    packages=['MsTeamsConnector'],
    url='https://pypi.org/project/MsTeamsConnector/',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    author='Kirill Kravchenko',
    author_email='',
    description='',
    install_requires=['setuptools','requests', 'msal', 'pydantic']
)
