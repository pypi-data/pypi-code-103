import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='opencontest-client',
    version='2.1.0',
    author='Anthony Wang',
    author_email='ta180m@pm.me',
    description='A very simple OpenContest command line client written in Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/LadueCS/OpenContest-Client',
    py_modules=[ 'main' ],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent'
    ],
    entry_points={
        'console_scripts': [
            'occ = main:__main__',
        ],
    },
    install_requires=[
        'requests'
    ]
)
