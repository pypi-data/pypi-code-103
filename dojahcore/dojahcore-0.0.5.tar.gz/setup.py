from setuptools import setup, find_packages
from os import path



VERSION = '0.0.5' 
DESCRIPTION = 'The official Dojah Core Python package'


current_dir = path.abspath(path.dirname(__file__))
with open(path.join(current_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="dojahcore", 
        version=VERSION,
        author="Dojah",
        author_email="taiwo@dojah.io",
        description=DESCRIPTION,
        long_description=long_description,
        long_description_content_type="text/markdown",
        packages=find_packages(exclude=["*.tests","*.tests.*"]),
        install_requires=[
            "requests",
            "python-dotenv"
        ], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'dojah', 'kyc','verification'],
        classifiers= [
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
        ]
)