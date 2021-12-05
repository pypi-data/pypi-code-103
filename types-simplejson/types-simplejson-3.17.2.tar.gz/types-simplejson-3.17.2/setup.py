from setuptools import setup

name = "types-simplejson"
description = "Typing stubs for simplejson"
long_description = '''
## Typing stubs for simplejson

This is a PEP 561 type stub package for the `simplejson` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `simplejson`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/simplejson. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `2610c5ee379ef2acfc964857544929097ac704a1`.
'''.lstrip()

setup(name=name,
      version="3.17.2",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=[],
      packages=['simplejson-stubs'],
      package_data={'simplejson-stubs': ['__init__.pyi', 'decoder.pyi', 'encoder.pyi', 'errors.pyi', 'raw_json.pyi', 'scanner.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Typed",
      ]
)
