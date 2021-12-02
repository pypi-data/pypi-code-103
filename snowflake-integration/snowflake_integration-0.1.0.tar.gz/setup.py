from setuptools import setup

setup(
    name='snowflake_integration',
    version='0.1.0',    
    description='Its a package to integrate snowflake with sagemaker',
    author='Shubham Setia',
    author_email='shubham.setia.3701@gmail.com',    
    license='BSD 2-clause',
    packages=['snowflake_integration'],
    setup_requires=['wheel'],
    install_requires=['numpy','pandas','snowflake','boto3','snowflake-connector-python[secure-local-storage,pandas]',
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