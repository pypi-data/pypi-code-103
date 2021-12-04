from setuptools import setup

name = "types-paramiko"
description = "Typing stubs for paramiko"
long_description = '''
## Typing stubs for paramiko

This is a PEP 561 type stub package for the `paramiko` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `paramiko`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/paramiko. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `f105c7921951d19e0a9a3a9ae1726bea25e98e4d`.
'''.lstrip()

setup(name=name,
      version="2.8.3",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=['types-cryptography'],
      packages=['paramiko-stubs'],
      package_data={'paramiko-stubs': ['__init__.pyi', '_version.pyi', '_winapi.pyi', 'agent.pyi', 'auth_handler.pyi', 'ber.pyi', 'buffered_pipe.pyi', 'channel.pyi', 'client.pyi', 'common.pyi', 'compress.pyi', 'config.pyi', 'dsskey.pyi', 'ecdsakey.pyi', 'ed25519key.pyi', 'file.pyi', 'hostkeys.pyi', 'kex_curve25519.pyi', 'kex_ecdh_nist.pyi', 'kex_gex.pyi', 'kex_group1.pyi', 'kex_group14.pyi', 'kex_group16.pyi', 'kex_gss.pyi', 'message.pyi', 'packet.pyi', 'pipe.pyi', 'pkey.pyi', 'primes.pyi', 'proxy.pyi', 'py3compat.pyi', 'rsakey.pyi', 'server.pyi', 'sftp.pyi', 'sftp_attr.pyi', 'sftp_client.pyi', 'sftp_file.pyi', 'sftp_handle.pyi', 'sftp_server.pyi', 'sftp_si.pyi', 'ssh_exception.pyi', 'ssh_gss.pyi', 'transport.pyi', 'util.pyi', 'win_pageant.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Typed",
      ]
)
