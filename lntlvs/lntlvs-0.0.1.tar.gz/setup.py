import os

import setuptools


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()

setuptools.setup(
    name='lntlvs',
    version='0.0.1',
    description=
    'Extract custom metadata records that may have been attached to lightning payments you received',
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url='https://github.com/seetee-io/lntlvs',
    author='@dnlggr',
    author_email='hello@seetee.io',
    license='GPL-3.0-only',
    entry_points={
        'console_scripts': ['lntlvs=lntlvs.cli:main'],
    },
    install_requires=[
        'click>=8.0.3,<9', 'grpcio>=1.42,<2',
        'googleapis-common-protos>=1.53,<2'
    ],
    extras_require={'dev': ['grpcio-tools>=1.42,<2']},
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
)
