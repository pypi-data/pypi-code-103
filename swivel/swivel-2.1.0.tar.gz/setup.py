from setuptools import setup, find_packages

with open('README.md', 'r') as file:
    long_description = file.read()

test_deps = [
    'pytest==6.2.5',
    'eth-tester==0.5.0b4',
    'web3==5.23.1',
    'py-eth-sig-utils==0.4.0',
]

extras = {
    'test': test_deps,
}

setup(
    name='swivel',
    version='2.1.0',
    author='Swivel Finance',
    author_email='support@swivel.finance',
    description='A python library for interacting with the Swivel Finance Protocol',
    long_description=long_description,
    keywords='swivel, finance, ethereum, blockchain, defi, web3',
    long_description_content_type='text/markdown',
    url='https://github.com/Swivel-Finance/swivel-py',
    packages=find_packages(exclude='tests'),
    python_requires='>=3.7.3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    tests_require=test_deps,
    extras_require=extras,
)
