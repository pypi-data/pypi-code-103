#!/usr/bin/env python


if __name__ == "__main__":
    import setuptools
    setuptools.setup(
        name='django-logger-test',
        packages=['logger'],
        version='1.3.5',
        install_requires=[
            'Django',
        ]
    )
