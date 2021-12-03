from setuptools import setup

setup(
    name='results_reader',
    version="0.0.2",
    packages=['cli'],
    entrypoints = {
        'console_scripts': [
            'cli = cli.__main__:main'
        ]
    }
)
