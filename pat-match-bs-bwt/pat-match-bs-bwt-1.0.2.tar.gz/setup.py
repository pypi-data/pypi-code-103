from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()

long_description = 'This package creates a suffix array and then the search can be performed using Improved Binary Search' \
                   'or using Burrows-Wheeler Transform FM index array'

setup(
    name='pat-match-bs-bwt',
    version='1.0.2',
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
            'search-bs=scripts.search_bs:main',
            'search-bw=scripts.search_bw:main'
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