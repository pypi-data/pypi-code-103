from setuptools import setup

setup(
    name='connect-snowflake',
    version='0.1.0',    
    description='A Python package to connect snowflake',
    url='https://github.com/shuds13/pyexample',
    author='Abhishek',
    
    license='BSD 2-clause',
    packages=['snowflake_connection'],
    install_requires=['snowflake-connector-python==2.7.0',
                      'pyarrow==5.0.0',                     
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)