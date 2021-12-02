__copyright__ = """
* Copyright (c) 2018 CA. All rights reserved.
*
* This software and all information contained therein is confidential and proprietary and
* shall not be duplicated, used, disclosed or disseminated in any way except as authorized
* by the applicable license agreement, without the express written permission of CA. All
* authorized reproductions must be marked with this language.
*
* EXCEPT AS SET FORTH IN THE APPLICABLE LICENSE AGREEMENT, TO THE EXTENT
* PERMITTED BY APPLICABLE LAW, CA PROVIDES THIS SOFTWARE WITHOUT WARRANTY
* OF ANY KIND, INCLUDING WITHOUT LIMITATION, ANY IMPLIED WARRANTIES OF
* MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. IN NO EVENT WILL CA BE
* LIABLE TO THE END USER OR ANY THIRD PARTY FOR ANY LOSS OR DAMAGE, DIRECT OR
* INDIRECT, FROM THE USE OF THIS SOFTWARE, INCLUDING WITHOUT LIMITATION, LOST
* PROFITS, BUSINESS INTERRUPTION, GOODWILL, OR LOST DATA, EVEN IF CA IS
* EXPRESSLY ADVISED OF SUCH LOSS OR DAMAGE.
"""
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

pwd = path.abspath(path.dirname(__file__))

with open(path.join(pwd, 'LICENSE.txt'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ca-apm-agent',

    # Using version number from git tag
    # use_scm_version={"root": "..", "relative_to": __file__},
    version_format='{tag}.dev{commitcount}',
    setup_requires=['setuptools-git-version'],

    description='Python Agent for CA APM',
    long_description='Install by running:\n\n ``sudo pip install ca-apm-agent``\n\n' +
                     'Visit `CA DocOps <http://docops.ca.com/rest/ca/product/latest/topic?hid=HID_Python&space=APMSAAS&language=&format=rendered>`_ ' +
                     'for additional details\n\n' + long_description,

    # The project's main homepage.
    url='http://docops.ca.com/rest/ca/product/latest/topic?hid=HID_Python&space=APMSAAS&language=&format=rendered',

    # Author details
    author='CA, Inc.',
    author_email='TeamAPMLeo@ca.com',

    # Choose your license
    license='See package description',
	
	# Supported Python ranges
	python_requires='>=3.0',	

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Keep updating supported frameworks here

        'Framework :: Django',
	'Framework :: Flask',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',

        # Pick your license as you wish (should match "license" above)
        'License :: Other/Proprietary License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
    ],

    # Project associated keywords - space separated
    keywords='ca-apm-agent application-performance-monitoring APM apm CA',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['docs', 'tests']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    include_package_data=True,
    package_data={
        'directives': ['directives/agent.profile, directives/instrument.pbd'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],
    data_files=[],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'ca-apm-runpy=ca_apm_agent:main',
        ],
    },
)
