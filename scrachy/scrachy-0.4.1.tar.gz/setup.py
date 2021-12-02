#  Copyright 2020 Reid Swanson.
#
#  This file is part of scrachy.
#
#  scrachy is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  scrachy is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with scrachy.  If not, see <https://www.gnu.org/licenses/>.

# Python Modules
import pathlib

from setuptools import find_packages, setup

# 3rd Party Modules

# Project Modules


current_dir = pathlib.Path(__file__).parent
readme = (current_dir / "README.md").read_text()

if __name__ == '__main__':
    setup(
        name='scrachy',
        version='0.4.1',
        description='Enhanced caching modules for scrapy.',
        long_description=readme,
        long_description_content_type='text/markdown',
        install_requires=[
            'beautifulsoup4',
            'diff-match-patch',
            'scrapy',
            'sqlalchemy',
            'w3lib'
        ],
        extras_require={
            'content-extraction-extensions': [
                'boilerpy3'
            ],
            'html-parsing-extensions': [
                'html5lib',
                'lxml'
            ],
            'mysql': [
                'mysql_python',  # python 2 only
                'mysqlclient'    # python 3 compatible
            ],
            'postgresql': [
                'psycopg2'
            ],
            'simhash': [
                # Note this requires the version from git (not PyPi) for python 3
                # 'simhash-py @ git+https://github.com/seomoz/simhash-py.git#egg=simhash-py'

                # However, you can't have a direct dependency and upload to PyPI.
                # So, I'll keep the PyPI version as the dependency even though
                # the user will need to manually update it to use the git
                # version.
                'simhash-py'
            ],
            'tokenization-extensions': [
                'blingfire'
            ],
            'hashing-extensions': [
                'spookyhash',
                'xxhash'
            ]
        },
        author='Reid Swanson',
        maintainer='Reid Swanson',
        author_email='reid@reidswanson.com',
        maintainer_email='reid@reidswanson.com',
        zip_safe=False,
        packages=find_packages(),
        include_package_data=True,
        license='lgpl-v3',
        url='https://bitbucket.org/reidswanson/scrachy',
        classifiers=['Development Status :: 4 - Beta',
                     'Intended Audience :: Science/Research',
                     'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
                     'Natural Language :: English',
                     'Operating System :: MacOS',
                     'Operating System :: Microsoft :: Windows',
                     'Operating System :: POSIX',
                     'Operating System :: Unix',
                     'Programming Language :: Python :: 3.7',
                     'Programming Language :: Python :: 3.8'])
