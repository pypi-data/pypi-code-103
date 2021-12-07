from setuptools import find_packages, setup
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / 'README.md').read_text()

setup(
    name='webpilot',
    packages=find_packages(include=['webpilot']),
    version='0.3.0',
    description='Api to control chromium browsers using puppeteer',
    long_description=README,
    long_description_content_type='text/markdown',
    author='fernandojerez',
    license='Apache',
    requires=['websocket_client', 'pydantic', 'beautifulsoup4'],
    install_requires=["websocket_client", 'pydantic', 'beautifulsoup4'],
    test_suite='tests'
)
