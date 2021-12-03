import os
import re
import setuptools


with open('README.md', 'r') as rf:
    with open('CHANGELOG.md', 'r') as cf:
        long_description = rf.read() + cf.read()


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()

    return re.search('__version__ = [\'"]([^\'"]+)[\'"]', init_py).group(1)


version = get_version('wcd_geo_db')


setuptools.setup(
    name='wc-django-geo-db',
    version=version,
    author='WebCase',
    author_email='info@webcase.studio',
    license='MIT License',
    description='Geographical database for internal projects.',
    install_requires=(
        'fuzzywuzzy[speedup]==0.18.0',
        'px-settings==0.1.2',
        'px-client-builder==0.1.0',
        'px-django-postgres==0.1.0',
        'px-django-tree==0.1.1',
        'px-django-lingua==0.1.5',
        'requests>=2.0.0,<3.0.0',
        'pandas==1.2.4',
        'openpyxl==3.0.7',
        'xlrd==2.0.1',
    ),
    extras_require={
        'dev': (
            'pytest>=6.0,<7.0',
            'pytest-watch>=4.2,<5.0',
            'pytest-django>=4.3,<5.0',
            'django-environ==0.4.5',
            'django-stubs',
            'django-silk>=4.2.0<5.0',
            'django>=2.2,<4',
            'twine',
        ),
        'dal': (
            'django-autocomplete-light>=3.9.0rc5,<4.0',
            'djhacker>=0.1.2,<0.2',
        ),
        'sources': (
            'wc-novaposhta==0.1.0',
            'wc-delivery-auto-sdk==0.1.0',
        )
    },
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(exclude=(
        'tests', 'tests.*',
        'experiments', 'pilot',
    )),
    python_requires='>=3.6',
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',

        'Programming Language :: Python :: 3',

        'Intended Audience :: Developers',
        'Topic :: Utilities',

        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ),
)
