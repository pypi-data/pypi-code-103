from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()

long_description = 'This package contains the naive suffix-tree implementation \
                   which tries to find the pattern in the given string'

setup(
    name='pat-match-st',
    version='1.0.4',
    author='Balraj Singh Saini, Chahat Gupta, Janardhan Jayachandra Kammath',
    author_email='au671472@post.au.dk',
    url='https://github.com/balrajsingh9/gsa-projects',
    description='pattern matching tools',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'search-st=scripts.search_st:main',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    zip_safe=False
)