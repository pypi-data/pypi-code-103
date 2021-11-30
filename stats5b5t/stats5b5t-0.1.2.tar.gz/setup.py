from setuptools import setup, find_packages

VERSION = '0.1.2' 
DESCRIPTION = 'API Wrapper for 5b5t.org'
LONG_DESCRIPTION = """Automate and simplify API requests for 5b5t.org.
A detailed documentation can be found at https://github.com/ScobraScope/stats5b5t-documentation
"""

setup(
       # the name must match the folder name 'verysimplemodule'
        name="stats5b5t", 
        version=VERSION,
        author="ScobraScope",
        url="https://github.com/ScobraScope/stats5b5t",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[
            "requests"
        ],
        keywords=['python', 'api', '5b5t', 'minecraft'],
        classifiers= [
            "Operating System :: Microsoft :: Windows",
            "Intended Audience :: Developers",
            "Intended Audience :: Education",
            "Natural Language :: English",
            "Programming Language :: Python :: 3.9",
            "Topic :: Games/Entertainment", 
        ]
)