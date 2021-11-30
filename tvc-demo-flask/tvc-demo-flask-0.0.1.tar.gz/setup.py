from setuptools import setup
setup(
    name='tvc-demo-flask',
    url='https://github.com/tanajivchavan/python-flask', 
    author='Tanaji Chavan',
    author_email='tanajic@cybage.com',
    version='0.0.1',
    packages=['demo'],
    install_requires=[
        'requests',
        'importlib; python_version == "3.9.6"',
    ],
)
