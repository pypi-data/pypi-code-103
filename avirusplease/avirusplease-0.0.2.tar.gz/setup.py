from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()
setup(
    name='avirusplease',     # Name of the package. This is what people will be installing
    version='0.0.2',     # Version. Usually if you are not planning on making any major changes after this 1.0.0 is a good way to go.
    description='',     # Short description
    license='BSD 3-clause license',  
    maintainer='Tobias Olsen',
    long_description=long_description,     # This just makes your README.md the description shown on pypi
    long_description_content_type='text/markdown',
    maintainer_email='youremail@stats.ox.ac.uk',
    include_package_data=True,     # If you have extra (non .py) data this should be set to True 
    packages=find_packages(include=('avirusplease', 'avirusplease/*')),     # Where to look for the python package
    install_requires=[     # All Requirements
        'numpy',
    ],
)
