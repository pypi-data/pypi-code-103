import setuptools

with open("README.md", 'r') as fh:
    long_description = fh.read()
setuptools.setup(
    name = 'checkfuncs',
    version = '1.0.0',
    author = 'fuqiang',
    author_email = 'fq1403082595@gmail.com',
    packages = setuptools.find_packages()

)