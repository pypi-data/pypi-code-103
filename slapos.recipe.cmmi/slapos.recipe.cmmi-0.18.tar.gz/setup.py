from setuptools import setup, find_packages
import os

version = '0.18'
name = 'slapos.recipe.cmmi'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name=name,
    version=version,
    description="zc.buildout recipe for compiling and installing source distributions.",
    long_description=(
        read('README.rst')
        + '\n' +
        read('CHANGELOG.rst')
        + '\n' +
        read('slapos', 'recipe', 'cmmi', 'README.rst')
        + '\n' +
        'Download\n'
        '========\n'
    ),
    classifiers=[
        'Framework :: Buildout :: Recipe',
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='development buildout recipe',
    author='Nexedi',
    author_email='info@nexedi.com',
    url='https://lab.nexedi.com/nexedi/slapos.recipe.cmmi',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['slapos', 'slapos.recipe'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'zc.buildout>=2',
        'setuptools',
        'slapos.recipe.build>=0.49',
    ],
    extras_require={
        'test': ['zope.testing', 'manuel'],
    },
    tests_require=['zope.testing', 'manuel'],
    test_suite='slapos.recipe.cmmi.tests.test_suite',
    entry_points={'zc.buildout': ['default = slapos.recipe.cmmi:Recipe']},
)
