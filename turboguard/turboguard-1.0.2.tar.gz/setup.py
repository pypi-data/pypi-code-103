import re
from os.path import join, dirname

from setuptools import setup, Extension


# reading package version (same way the sqlalchemy does)
HERE = dirname(__file__)
with open(join(HERE, 'turboguard', '__init__.py')) as v_file:
    package_version = re.compile('.*__version__ = \'(.*?)\'', re.S).\
        match(v_file.read()).group(1)


dependencies = []


core = Extension(
    'turboguard.core',
    sources=['turboguard/core.c']
)

setup(
    name='turboguard',
    version=package_version,
    packages=['turboguard'],
    install_requires=dependencies,
    ext_modules=[core],

    # Info
    license='MIT',
    author='Vahid Mardani',
    author_email='vahid.mardani@gmail.com',
    url='http://github.com/pylover/turboguard',
    description='Fast Unicode mapping and character blacklists using Python '
                'C extension.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',

    # Classifiers
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
