from setuptools import setup

setup(
    name='goodow-dataflow',
    version='0.3.0',
    packages=['goodow'],
    install_requires=[
        'requests',
        'importlib; python_version == "3.10"',
    ],
)