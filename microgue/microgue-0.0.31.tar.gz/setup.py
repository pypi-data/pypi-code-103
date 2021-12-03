from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name='microgue',
    version='0.0.31',
    author='Michael Hudelson',
    author_email='michaelhudelson@gmail.com',
    description='Quickly spin up microservices in AWS using flask',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'boto3',
        'flask',
        'flask-classful',
        'redis',
        'requests'
    ],
    python_requires=">=3.6",
)
