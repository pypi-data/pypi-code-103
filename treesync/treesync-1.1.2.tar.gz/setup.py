
from setuptools import setup, find_packages
from treesync import __version__

setup(
    name='treesync',
    keywords='directory rsync backup utility',
    description='Utilitiies to use rsync for whole trees',
    author='Ilkka Tuohela',
    author_email='hile@iki.fi',
    url='https://git.tuohela.net/python/pathlib-tree',
    version=__version__,
    license='PSF',
    python_requires='>3.6.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'treesync=treesync.bin.treesync.main:main',
        ],
    },
    install_requires=(
        'pathlib-tree>=1.1.0',
    ),
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3',
        'Topic :: System',
        'Topic :: System :: Systems Administration',
    ],
)
