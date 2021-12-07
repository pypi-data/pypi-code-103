from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'PrimeNumberChecker'
LONG_DESCRIPTION = 'Enter the number and check if the number is prime or not'

# Setting up
setup(
        name="checkprimenumbers", 
        version=VERSION,
        author="Sandesh Dhakal",
        author_email="dhakalsandesh5@gmail.com",
        url="https://github.com/sandesh8888/prime-numbers",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], 
        license='BSD 2-clause',
        keywords=['python', 'first package'],
        classifiers= [
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: Microsoft :: Windows",
        ]
)