import setuptools
import os


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as fp:
        s = fp.read()
    return s


def get_version(path):
    with open(path, "r") as fp:
        lines = fp.read()
    for line in lines.split("\n"):
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name='node-distance',
    version=get_version("node_distance/__init__.py"),
    description=(
        "Compute distance between all nodes of a tree, and estimate an "
        "histogram that can be used as features for other models."),
    long_description=read('README.rst'),
    url='http://github.com/satzbeleg/node-distance',
    author='Ulf Hamster',
    author_email='554c46@gmail.com',
    license='Apache License 2.0',
    packages=['node_distance'],
    install_requires=[
        'numpy>=1.19.5,<2',
        'networkx>=2.5.1,<3'
    ],
    python_requires='>=3.6',
    zip_safe=True
)
