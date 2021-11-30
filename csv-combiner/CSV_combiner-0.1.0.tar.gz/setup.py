from setuptools import setup

setup(
    name='CSV_combiner',
    version='0.1.0',    
    description='Tool to compine multiple csv files into one file',
    url='https://github.com/mo0haned/CSV-combiner',
    author='Mohaned AbdElMonsef, Mohammed Magdy',
    author_email='mo0han3d@gmail.com',
    license='BSD 2-clause',
    packages=['CSV_combiner'],
    install_requires=['pandas'],

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
    ],
)