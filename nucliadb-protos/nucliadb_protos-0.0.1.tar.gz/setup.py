from setuptools import find_packages, setup


long_description = open("README.rst").read() + "\n"
changelog = open("CHANGELOG.rst").read()
found = 0
for line in changelog.splitlines():
    if len(line) > 15 and line[-1] == ")" and line[-4] == "-":
        found += 1
        if found >= 20:
            break
    long_description += "\n" + line


long_description += """

...

You are seeing a truncated changelog.

You can read the `changelog file <https://github.com/nuclia/nucliadb/blob/master/nucliadb_protos/python/CHANGELOG.rst>`_
for a complete list.

"""

setup(
    name="nucliadb_protos",
    version=open("VERSION").read().strip(),
    description="protos for nucliadb",  # noqa
    long_description=long_description,
    setup_requires=["pytest-runner"],
    zip_safe=True,
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'protobuf',
        'grpcio',
        'grpcio-tools>=1.31.0',
        'mypy-protobuf>=3.0.0'
    ],
)
