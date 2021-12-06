from setuptools import setup

name = "types-flake8-simplify"
description = "Typing stubs for flake8-simplify"
long_description = '''
## Typing stubs for flake8-simplify

This is a PEP 561 type stub package for the `flake8-simplify` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `flake8-simplify`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/flake8-simplify. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `34721fcadc52a9230b10c38413da78e5168b2a35`.
'''.lstrip()

setup(name=name,
      version="0.14.1",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=[],
      packages=['flake8_simplify-stubs'],
      package_data={'flake8_simplify-stubs': ['__init__.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Typed",
      ]
)
