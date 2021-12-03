from os import environ as envvars
from pathlib import Path
from setuptools import find_packages
from setuptools import setup


setup(
    name='sanka',
    description='a function decorator for surfacing dead code',
    license='MIT',
    long_description=Path(__file__).absolute().parent.joinpath('README.md').read_text(),
    long_description_content_type='text/markdown',
    use_scm_version={'local_scheme': 'no-local-version'} if envvars.get('LOCAL_VERSION_SCHEME') else True,
    author='Emmanuel I. Obi',
    maintainer='Emmanuel I. Obi',
    maintainer_email='withtwoemms@gmail.com',
    url='https://github.com/withtwoemms/sanka',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    py_modules=['sanka'],
    setup_requires=[
        'setuptools_scm==5.0.1'
    ],
)
