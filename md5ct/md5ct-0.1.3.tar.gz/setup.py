import os

import setuptools
import md5ct
from pypinyin import pinyin, lazy_pinyin, Style


def _process_requirements():
    packages = open('requirements.txt').read().strip().split('\n')
    requires = []
    for pkg in packages:
        if pkg.startswith('git+ssh'):
            return_code = os.system('pip install {}'.format(pkg))
            assert return_code == 0, 'error, status_code is: {}, exit!'.format(return_code)
        else:
            requires.append(pkg)
    return requires


with open("README.md", "r", encoding='UTF-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="md5ct",
    version=md5ct.__VERSION__,
    author="xiongyu",
    author_email="ixiongyu@gmail.com",
    description="a md5 batch change tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ixiongyu/md5changer",
    packages=setuptools.find_packages(),
    keywords='MD5',
    py_modules=['md5ct'],
    entry_points={
        'console_scripts': ['md5ct=md5ct:cli'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
