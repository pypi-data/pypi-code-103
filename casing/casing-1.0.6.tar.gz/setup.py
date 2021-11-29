from distutils.core import setup
import os
import sys

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='casing',
    version="1.0.6",
    author='Vincent Bénet',
    author_email='vincent.benet@outlook.fr',
    url='https://github.com/vincentBenet/casing',
    description='Easy casing nomenclatures management such as camelCase, snake_case and many others!',
    keywords=['casing', 'snake_case', 'camelCase', 'case', 'python'],
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
    ],
    packages=["casing"],
    include_package_data=True,
    long_description="""
    
Casing
==========

This project aim to manage automatically you casing names of variables.

Usage
-----------

There is 3 functions that you save you time:
    
`casing.analyse` will parse your string.

    >>> casing.analyze("stringToDetect")
    >>> ['string', 'to', 'detect']
    
`casing.transform` will transform a string or a list into a casing.

    >>> casing.transform("stringToDetect", case="snake")
    >>> "string_to_detect"
    
    >>> casing.transform(['string', 'to', 'detect'], case="snake")
    >>> "string_to_detect"

`casing.detect` will detect the casing of a string.

    >>> casing.detect("string_to_detect")
    >>> "snake"
    

Options
-----------

You can switch between all this cases:

attachedcase: stringtodetect 
attacheduppercase: STRINGTODETECT 
camelcase: stringToDetect    
dashcase: string-to-detect   
dashuppercase: STRING-TO-DETECT   
normalcase: string to detect 
normaluppercase: STRING TO DETECT 
pascalcase: StringToDetect   
prettycase: String To Detect 
reversedcase: string To Detect    
sentencecase: String to detect    
snakecase: string_to_detect  
snakeuppercase: STRING_TO_DETECT
    
    """,
    # scripts=["casing.py"]
)

# python setup.py sdist 
# twine upload dist/* 