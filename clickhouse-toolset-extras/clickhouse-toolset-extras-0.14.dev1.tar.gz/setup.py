from setuptools import setup, Extension

NAME = 'clickhouse-toolset'
VERSION = '0.14.dev1'

try:
    from conf import *
    chquery = Extension(
        'chtoolset._query',
        sources=['src/query.cpp'],
        depends=['src/ClickHouseQuery.h'],
        include_dirs=include_dirs,
        extra_compile_args=['-std=gnu++20'],
        library_dirs=library_dirs,
        libraries=libraries
    )
    setup(
        name=NAME,
        version=VERSION,
        url='https://gitlab.com/tinybird/clickhouse-toolset',
        author='Tinybird.co',
        author_email='support@tinybird.co',
        packages=['chtoolset'],
        package_dir={'': 'src'},
        python_requires='>=3.6, <3.11',
        install_requires=[],
        extras_require={
            'test': requirements_from_file('requirements-test.txt')
        },
        cmdclass={
            'clickhouse': ClickHouseBuildExt,
            'build_ext': CustomBuildWithClang,
        },
        ext_modules=[chquery]
    )

except ModuleNotFoundError:
    setup(
        name=NAME,
        version=VERSION,
        url='https://gitlab.com/tinybird/clickhouse-toolset',
        author='Tinybird.co',
        author_email='support@tinybird.co',
        packages=['chtoolset'],
        package_dir={'': 'src'},
        python_requires='>=3.6, <3.11',
        install_requires=[],
    )
