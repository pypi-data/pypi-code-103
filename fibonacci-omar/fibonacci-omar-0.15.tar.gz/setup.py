from os.path import dirname, join
from setuptools import find_packages, setup


AUTHOR = 'Omar Elazhary'
AUTHOR_EMAIL = 'omar.elazhary@motorolasolutions.com'
LICENSE = 'MIT'
SHORT_DESCRIPTION = 'Plays around with Fibonacci sequences.'
WORKING_DIR = dirname(__file__)
VERSION_FILE = join(WORKING_DIR, 'VERSION')


with open('README.md', 'r', encoding='utf-8') as long_description_in:
    long_description = long_description_in.read().strip()

with open(VERSION_FILE, 'r', encoding='utf-8') as version_in:
    version_raw = version_in.read().strip()
    version_components = version_raw.split('.')
    version = version_components[0] + '.' + str(int(version_components[1]) + 1)

setup(
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    name='fibonacci-omar',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    description=SHORT_DESCRIPTION,
    description_content_type='text/markdown',
    install_requires=[],
    keywords='fibonacci sequence',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    python_requires='>=3.9',
    scripts=[
        'bin/fibonacci'
    ],
    url='https://reposherlock.readthedocs.io/en/latest/index.html',
    version=version,
    zip_safe=False
)

with open(VERSION_FILE, 'w', encoding='utf-8') as version_out:
    version_out.write(version)
