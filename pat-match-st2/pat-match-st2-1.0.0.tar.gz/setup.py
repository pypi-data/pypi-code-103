from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()

long_description = 'This package creates a suffix tree and then generates suffix-array and lcp-array using gen-lcp.' \
                   'search-st2 creates a suffix tree in linear time using the suffix array and lcp-array generated' \
                   'by the gen-lcp'

setup(
    name='pat-match-st2',
    version='1.0.0',
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
            'gen-lcp=scripts.gen_lcp:main',
            'search-st2=scripts.search_st2:main'
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