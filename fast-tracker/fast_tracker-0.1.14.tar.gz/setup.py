# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import os

python_version = sys.version_info[:2]

assert python_version in ((2, 7),) or python_version >= (3, 5), \
    '天眼Python探针只支持 Python 2.7 and 3.5+.'

with_setuptools = False

try:
    from setuptools import setup

    with_setuptools = True
except ImportError:
    from distutils.core import setup

from distutils.core import Extension
from distutils.command.build_ext import build_ext
from distutils.errors import (CCompilerError, DistutilsExecError,
                              DistutilsPlatformError)


script_directory = os.path.dirname(__file__)
if not script_directory:
    script_directory = os.getcwd()

readme_file = os.path.join(script_directory, 'README.rst')

if sys.platform == 'win32' and python_version > (2, 6):
    build_ext_errors = (CCompilerError, DistutilsExecError,
                        DistutilsPlatformError, IOError)
else:
    build_ext_errors = (CCompilerError, DistutilsExecError,
                        DistutilsPlatformError)


class BuildExtFailed(Exception):
    pass


class optional_build_ext(build_ext):
    def run(self):
        try:
            build_ext.run(self)
        except DistutilsPlatformError:
            raise BuildExtFailed()

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except build_ext_errors:
            raise BuildExtFailed()


packages = [
    "fast_tracker",
    "fast_tracker.admin",
    "fast_tracker.api",
    "fast_tracker.bootstrap",
    "fast_tracker.common",
    "fast_tracker.core",
    "fast_tracker.extras",
    "fast_tracker.extras.framework_django",
    "fast_tracker.extras.framework_django.templatetags",
    "fast_tracker.hooks",
    "fast_tracker.network",
    "fast_tracker/packages",
    "fast_tracker/packages/google",
    "fast_tracker/packages/google/protobuf",
    "fast_tracker/packages/google/protobuf/compiler",
    "fast_tracker/packages/google/protobuf/internal",
    "fast_tracker/packages/google/protobuf/internal/import_test_package",
    "fast_tracker/packages/google/protobuf/pyext",
    "fast_tracker/packages/google/protobuf/util",
    "fast_tracker/packages/log",
    "fast_tracker/packages/requests",
    "fast_tracker/packages/requests/packages",
    "fast_tracker/packages/requests/packages/chardet",
    "fast_tracker/packages/requests/packages/urllib3",
    "fast_tracker/packages/requests/packages/urllib3/packages",
    "fast_tracker/packages/requests/packages/urllib3/packages/ssl_match_hostname",
    "fast_tracker/packages/requests/packages/urllib3/util",
    "fast_tracker/packages/wrapt",
    "fast_tracker.samplers",
]

classifiers = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Topic :: System :: Monitoring",
]

kwargs = dict(
    name="fast_tracker",
    version='0.1.14',
    setup_requires=['setuptools_scm'],
    description="FAST Python Agent",
    long_description=open(readme_file).read(),
    url="http://doc.mypaas.com.cn/fast/03_%E6%9C%8D%E5%8A%A1%E7%AB%AF%E6%8E%A2%E9%92%88%E9%9B%86%E6%88%90/%E7%AE%80%E4%BB%8B.html",
    author="FAST",
    author_email="liulh01@mingyuanyun.com",
    maintainer='FAST',
    maintainer_email='liulh01@mingyuanyun.com',
    license='Apache-2.0',
    zip_safe=False,
    classifiers=classifiers,
    packages=packages,
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
    package_data={'fast_tracker': ['FastTracker.json',
                                   'version.txt',
                                   'common/cacert.pem',
                                   'packages/requests/LICENSE',
                                   'packages/requests/NOTICE',
                                   'packages/requests/cacert.pem'],
                  },
    scripts=['scripts/fast-admin'],
    extras_require={'infinite-tracing': ['grpcio<2', 'protobuf<4']},
)

if with_setuptools:
    kwargs['entry_points'] = {
        'console_scripts': ['fast-admin = fast_tracker.admin:main'],
    }


def with_librt():
    try:
        if sys.platform.startswith('linux'):
            import ctypes.util
            return ctypes.util.find_library('rt')
    except Exception:
        pass


def run_setup(with_extensions):
    def _run_setup():

        # Create a local copy of kwargs, if there is no c compiler run_setup
        # will need to be re-run, and these arguments can not be present.

        kwargs_tmp = dict(kwargs)

        if with_extensions:
            monotonic_libraries = []
            if with_librt():
                monotonic_libraries = ['rt']

            kwargs_tmp['ext_modules'] = [
                Extension("fast_tracker.packages.wrapt._wrappers",
                          ["fast_tracker/packages/wrapt/_wrappers.c"]),
                Extension("fast_tracker.common._monotonic",
                          ["fast_tracker/common/_monotonic.c"],
                          libraries=monotonic_libraries),
                Extension("fast_tracker.core._thread_utilization",
                          ["fast_tracker/core/_thread_utilization.c"]),
            ]
            kwargs_tmp['cmdclass'] = dict(build_ext=optional_build_ext)

        setup(**kwargs_tmp)

    if os.environ.get('TDDIUM') is not None:
        try:
            print('INFO: Running under tddium. Use lock.')
            from lock_file import LockFile
        except ImportError:
            print('ERROR: Cannot import locking mechanism.')
            _run_setup()
        else:
            print('INFO: Attempting to create lock file.')
            with LockFile('setup.lock', wait=True):
                _run_setup()
    else:
        _run_setup()


WARNING = """
WARNING: The optional C extension components of the Python agent could
not be compiled. This can occur where a compiler is not present on the
target system or the Python installation does not have the corresponding
developer package installed. The Python agent will instead be installed
without the extensions. The consequence of this is that although the
Python agent will still run, some non core features of the Python agent,
such as capacity analysis instance busy metrics, will not be available.
Pure Python versions of code supporting some features, rather than the
optimised C versions, will also be used resulting in additional overheads.
"""

with_extensions = os.environ.get('FAST_EXTENSIONS', None)
if with_extensions:
    if with_extensions.lower() == 'true':
        with_extensions = True
    elif with_extensions.lower() == 'false':
        with_extensions = False
    else:
        with_extensions = None

if hasattr(sys, 'pypy_version_info'):
    with_extensions = False

if with_extensions is not None:
    run_setup(with_extensions=with_extensions)

else:
    try:
        run_setup(with_extensions=True)

    except BuildExtFailed:

        print(75 * '*')

        print(WARNING)
        print("INFO: Trying to build without extensions.")

        print()
        print(75 * '*')

        run_setup(with_extensions=False)

        print(75 * '*')

        print(WARNING)
        print("INFO: Only pure Python agent was installed.")

        print()
        print(75 * '*')
