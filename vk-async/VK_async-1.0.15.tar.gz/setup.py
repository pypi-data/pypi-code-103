from io import open
from setuptools import setup

"""
:author: Yoko
:copyright: (c) 2021 Yoko
"""

version = '1.0.15'

long_description = '''Python lib for async requests to VK API with wait_for and cogs'''

setup(
    name='VK_async',
    version=version,

    author='Yoko',
    author_email='zartem01@gmail.ru',

    description=(
        u'Python module for writing bots for VK'
        u'(VK API wrapper)'
    ),
    long_description=long_description,
    # long_description_content_type='text/markdown',

    url='https://github.com/Yoko-0/VK_async',
    download_url='https://github.com/Yoko-0/VK_async.git',

    packages=['VK_async'],
    install_requires=['aiohttp', 'asyncio'],

    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
    ]
)
