from setuptools import setup

from procpath import __version__


setup(
    name             = 'Procpath',
    version          = __version__,
    author           = 'saaj',
    author_email     = 'mail@saaj.me',
    packages         = ['procpath', 'procpath.cmd'],
    license          = 'LGPL-3.0-only',
    description      = 'Procpath is a process tree analysis workbench',
    long_description = open('README.rst', 'rb').read().decode('utf-8'),
    keywords         = 'procfs jsonpath sqlite plotting',
    python_requires  = ">= 3.7",
    url              = 'https://heptapod.host/saajns/procpath',
    project_urls     = {
        'Source Code'   : 'https://heptapod.host/saajns/procpath',
        'Documentation' : 'https://procpath.readthedocs.io/',
        'Release Notes' : 'https://procpath.readthedocs.io/en/latest/history.html',
    },
    classifiers = [
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',
        'Topic :: System :: Monitoring',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
    ],
    entry_points     = {'console_scripts': ['procpath = procpath.cli:main']},
    install_requires = [
        'jsonpyth < 0.2',
        'pygal == 3.0.0.dev1',
    ],
    extras_require = {
        'manual' : [
            'sphinx >= 4, < 5',
            'sphinxcontrib-programoutput < 0.18',
        ],
    },
)
