#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import sys

from shutil import rmtree
from setuptools import setup, Command
# from setuptools import find_packages

# Package meta-data.
NAME = 'alfa_utilities'
DESCRIPTION = 'ALFA utilities for base detectors'
# This url points to the source code.
URL = 'https://svn.fra.syrocon.net:8181/scm/git/syrocon/ai-adas/machineLearning_env/alfa-utils-master'
VERSION = '0.2.7'
# This download url is not the one provided by PyPI. It's the one, that can be set within the github repo project.
DOWNLOAD_URL = f'{URL}/dist/alfa_utilities-{VERSION}.tar.gz'
EMAIL = 'tuananh.le@syrocon.de'
AUTHOR = 'Tuan Anh Le'
REQUIRES_PYTHON = '>=3.8'

# What packages are required for this module to be executed?
REQUIRED = [
    'numpy',
    'torch',
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system(
            '{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')

        sys.exit()


setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    download_url=DOWNLOAD_URL,
    # packages=find_packages(
    #     exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    # If your package is a single module, use this instead of 'packages'
    py_modules=['alfa_utils'],
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)
