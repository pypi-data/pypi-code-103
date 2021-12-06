from setuptools import setup

setup(
    name='goodow-workflow',
    version='0.3.0',
    packages=['goodow'],
    install_requires=[
        'requests',
        'importlib; python_version == "3.10"',
    ],
)