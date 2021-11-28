import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pyping2',
    url='https://github.com/awesomelewis2007/PyPing2/',
    author='Lewis Evans',
    author_email='awesomelewis2007@gmail.com',
    packages=['pyping2'],
    install_requires=[''],
    version="0.1.0",
    license='GNU',
    long_description=long_description,
    long_description_content_type="text/markdown",
    description='An easy to use pinging tool'
)