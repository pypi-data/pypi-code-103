from setuptools import setup
import os
setup(
    name='CollinImports',
    version=os.environ.get('IMPORTVERSION'),    
    description='My Packages',
    url='https://github.com/collinpu/CollinImports',
    author='Collin Purcell',
    author_email='collinpu@usc.edu',
    license='BSD 2-clause',
    packages=['CollinImports'],
    install_requires=['redis',
                      'numpy',                     
                      ],

    classifiers=[
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3'
    ],
)
