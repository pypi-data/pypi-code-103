import setuptools

setuptools.setup(
    name='iambcodes',
    version='0.0.5',
    author='Ulf Liebal',
    author_email='ulf.liebal@rwth-aachen.de',
    description='Functions for processing of Biolog data.',
    keywords='biolog',
    # url='https://git.rwth-aachen.de/ulf.liebal/FastaTools',
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    python_requires='>=3.6',
    install_requires=[
        'xlrd>=2.0.1',
        'numpy>=1.18.2',
        'cobra==0.17.1',
        'biopython>=1.78',
        'matplotlib>=3.3.4',
    ],
)
