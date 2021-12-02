# -*- coding: utf-8 -*-
"""Installer for the dsgov.migration package."""

from setuptools import find_packages
from setuptools import setup, Extension

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])

with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name='dsgov.migration',
    version='1.0b2',
    description="A migration package for DSGov-Plone5",
    long_description=long_description,
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone',
    author='Fabio Santos',
    author_email='fabio.santos@ifrr.edu.br',
    url='https://pypi.python.org/pypi/dsgov.migration',
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['dsgov'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        'plone.api>=1.8.4',
        'Products.GenericSetup>=1.8.2',
        'setuptools',
        'z3c.jbot',
        'pandas',
        'openpyxl',
        'collective.transmogrifier>=1.5.3.dev0',
        'plone.app.transmogrifier==1.4.2.dev0',
        'collective.jsonmigrator>=1.0.2.dev0',
        'transmogrify.dexterity==1.6.5.dev0',
    ],
    dependency_links=[
        'git+https://github.com/collective/collective.transmogrifier.git@python3#egg=collective.transmogrifier-1.5.3.dev0',
        'git+https://github.com/collective/collective.jsonmigrator.git@python3#egg=collective.jsonmigrator-1.0.2.dev0',
        'git+https://github.com/collective/plone.app.transmogrifier.git@python3#egg=plone.app.transmogrifier-1.4.2.dev0',
        'git+https://github.com/collective/transmogrify.dexterity.git@python3#egg=transmogrify.dexterity-1.6.5.dev0',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            'plone.testing>=5.0.0',
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = dsgov.migration.locales.update:update_locale
    """,
)
