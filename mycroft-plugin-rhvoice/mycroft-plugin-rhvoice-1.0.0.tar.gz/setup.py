#!/usr/bin/env python3
from setuptools import setup

TTS_ENTRY_POINT = 'rhvoice = mycroft_plugin_rhvoice:RHVoiceTTSPlugin'

readme = open('README.md', 'r')
README_TEXT = readme.read()
readme.close()

setup(
    name='mycroft-plugin-rhvoice',
    version='1.0.0',
    description='RHVoice TTS plugin for Mycroft',
    long_description=README_TEXT,
    long_description_content_type='text/markdown',
    url='https://github.com/putnik/mycroft-plugin-rhvoice',
    author='Sergey Leschina',
    author_email='mail@putnik.tech',
    license='Apache-2.0',
    packages=['mycroft_plugin_rhvoice'],
    zip_safe=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Text Processing :: Linguistic',
        'Natural Language :: Russian',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='mycroft plugin tts rhvoice',
    entry_points={
        'mycroft.plugin.tts': TTS_ENTRY_POINT,
    }
)
