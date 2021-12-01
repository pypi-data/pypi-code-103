from setuptools import setup

name = "types-redis"
description = "Typing stubs for redis"
long_description = '''
## Typing stubs for redis

This is a PEP 561 type stub package for the `redis` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `redis`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/redis. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `8542b3518a36313af57b13227996168e592fe868`.
'''.lstrip()

setup(name=name,
      version="4.0.3",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=[],
      packages=['redis-stubs'],
      package_data={'redis-stubs': ['__init__.pyi', 'client.pyi', 'commands/__init__.pyi', 'commands/core.pyi', 'commands/helpers.pyi', 'commands/json/__init__.pyi', 'commands/json/commands.pyi', 'commands/json/decoders.pyi', 'commands/json/path.pyi', 'commands/redismodules.pyi', 'commands/search/__init__.pyi', 'commands/search/commands.pyi', 'commands/sentinel.pyi', 'commands/timeseries/__init__.pyi', 'commands/timeseries/commands.pyi', 'commands/timeseries/info.pyi', 'commands/timeseries/utils.pyi', 'connection.pyi', 'exceptions.pyi', 'lock.pyi', 'retry.pyi', 'sentinel.pyi', 'utils.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Typed",
      ]
)
