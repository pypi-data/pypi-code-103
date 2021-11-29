from setuptools import setup, find_packages

def version():
    with open('VERSION', 'r') as fileobj:
        return fileobj.read()

def requirements():
    with open('requirements.txt', 'r') as fileobj:
        requirements = [line.strip() for line in fileobj]
        return requirements

setup(
    name='goss-sdk-python',
    version=version(),
    url='https://www.gizwits.com/',
    license='Apache',
    author='jzhuang',
    author_email='jzhuang@gizwits.com',
    description='goss-sdk-python',
    long_description='',
    packages=find_packages(),
    install_requires=requirements(),
)
