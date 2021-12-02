#It will govern the installation of your package. The setuptools package is recommended for this (the in-built distutils is an older alternative).

from setuptools import setup

setup(
    name='fil_package',
    version='0.1.0',    
    description='A Python package for addition',
    author='Shweta',
    author_email='swetakumari2002@gmail.com',
    license='BSD 2-clause',
    packages=['fil_package'],
    install_requires=['numpy',                     
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)