#!/usr/bin/env python

import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(name='polyaxon-trace',
      version='0.0.0',
      description='ML tracking and visualization librarie.',
      maintainer='Polyaxon, Inc.',
      maintainer_email='contact@polyaxon.com',
      author='Polyaxon',
      author_email='contact@polyaxon.com',
      url='https://github.com/polyaxon/trace',
      license='Apache 2.0',
      platforms='any',
      packages=find_packages(),
      cmdclass={'test': PyTest})
