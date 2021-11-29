import setuptools
import pathlib

setuptools.setup(
    name='pathimp',
    version='1.1.0',
    author='Danijar Hafner',
    author_email='mail@danijar.com',
    description='Import Python modules from any file system path.',
    url='http://github.com/danijar/pathimp',
    long_description=pathlib.Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    packages=['pathimp'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
