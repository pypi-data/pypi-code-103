"""The setup script."""

from setuptools import setup

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

setup(
    name='heaserver-people',
    version='1.0.0a1',
    description="A microservice designed to provide CRUD operations for the Person HEA object type",
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://risr.hci.utah.edu',
    author="Research Informatics Shared Resource, Huntsman Cancer Institute, Salt Lake City, UT",
    author_email='Andrew.Post@hci.utah.edu',
    python_requires='>=3.8',
    package_dir={'': 'src'},
    packages=['heaserver.person'],
    package_data={'heaserver.person': ['wstl/*.json']},
    install_requires=['heaserver>=1.0.0a38, <1.0.0a39'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Framework :: AsyncIO',
        'Environment :: Web Environment',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ],
    entry_points={
        'console_scripts': [
            'heaserver-people=heaserver.person.service:main',
        ],
    },
    keywords=['heaserver-people', 'microservice', 'healthcare', 'cancer', 'research', 'informatics'],
)
