from setuptools import find_packages, setup


setup(
    name='PyCTO',
    packages=find_packages(include=['numpy']),
    version='0.0.1',
    description='Prueba de Libreria para proyecto Global CTO',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author_email='eavila98@hotmail.com',
    author='KPMG Lighthouse'

)