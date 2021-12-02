from setuptools import setup

name = "types-psycopg2"
description = "Typing stubs for psycopg2"
long_description = '''
## Typing stubs for psycopg2

This is a PEP 561 type stub package for the `psycopg2` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `psycopg2`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/psycopg2. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `506be4fb0adcf38af77325258af337772abcde77`.
'''.lstrip()

setup(name=name,
      version="2.9.4",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=[],
      packages=['psycopg2-stubs'],
      package_data={'psycopg2-stubs': ['__init__.pyi', '_ipaddress.pyi', '_json.pyi', '_psycopg.pyi', '_range.pyi', 'errorcodes.pyi', 'errors.pyi', 'extensions.pyi', 'extras.pyi', 'pool.pyi', 'sql.pyi', 'tz.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Typed",
      ]
)
