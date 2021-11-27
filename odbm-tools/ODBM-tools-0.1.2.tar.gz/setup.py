from setuptools import setup

setup(
    name='ODBM-tools',
    version='0.1.2',    
    description='Optimization for Dynamic Bioconversion Modules',
    url='https://github.com/carothersresearch/ODBM',
    author='Diego Alba, Ryan Cardiff',
    author_email='dalba@uw.edu, cardiffr@uw.edu',
    license='MIT',
    packages=['odbm'],
    install_requires=['numpy', 'libroadrunner', 'pandas', 'regex','tellurium','overrides','matplotlib'],

    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
    ],
)