"""
Base module for operating system level tasks
"""

from setuptools import setup, find_packages
from sys_toolkit import __version__

setup(
    name='sys-toolkit',
    keywords='python operating system utility classes',
    description='Classes for operating system utilities',
    author='Ilkka Tuohela',
    author_email='hile@iki.fi',
    url='https://github.com/hile/sys-toolkit',
    version=__version__,
    license='PSF',
    python_requires='>3.6.0',
    packages=find_packages(),
    install_requires=(
        'PyYAML>=6.0',
        'pytz',
    ),
    entry_points={
        'pytest11': [
            'sys_toolkit_fixtures=sys_toolkit.fixtures',
        ]
    },
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3',
        'Topic :: System',
    ],
)
