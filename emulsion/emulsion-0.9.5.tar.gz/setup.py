"""Configuration for distributing the Emulsion package.

"""
from   setuptools import setup, find_packages

VERSION = "0.9.5"

setup(
    # This is the name of your project. The first time you publish this
    # package, this name will be registered for you. It will determine how
    # users can install this project, e.g.:
    #
    # $ pip install sampleproject
    #
    # And where it will live on PyPI: https://pypi.org/project/sampleproject/
    #
    # There are some restrictions on what makes a valid project name
    # specification here:
    # https://packaging.python.org/specifications/core-metadata/#name
    name='emulsion',       # Required
    # Versions should comply with PEP 440:
    # https://www.python.org/dev/peps/pep-0440/
    #
    # For a discussion on single-sourcing the version across setup.py and the
    # project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=VERSION, # Required
    license='CECILL-B',
    # This is a one-line description or tagline of what your project does. This
    # corresponds to the "Summary" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#summary
    description='A Python framework for Epidemiological Multi-Level Simulation',
    # This should be a valid link to your project's main homepage.
    #
    # This field corresponds to the "Home-Page" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#home-page-optional
    # url='https://github.com/pypa/emulsion',  # Optional
    # This should be your name or the name of the organization which owns the
    # project.
    author='Sébastien Picault, Yu-Lin Huang, Vianney Sicard and Pauline Ezanno',  # Optional
    # This should be a valid email address corresponding to the author listed
    # above.
    author_email='sebastien.picault@oniris-nantes.fr',  # Optional
    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Education',
        # Pick your license as you wish
        'License :: CeCILL-B Free Software License Agreement (CECILL-B)',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Unix Shell',
        # Specify the Operating Systems supported by your package
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix', # not tested in general - report bugs
        # Specify the environment
        'Environment :: Console',
        'Environment :: MacOS X',

    ],
    # This field adds keywords for your project which will appear on the
    # project page. What does your project relate to?
    #
    # Note that this is a string of words separated by whitespace, not a list.
    # keywords='computational_epidemiology, multilevel_modelling,'
    #   ' agent-based_simulation, animal_health',  # Optional

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    py_modules=[
        'emulsion/__main__',
        'emulsion/__init__',
        'emulsion/model',
        'emulsion/agent/__init__',
        'emulsion/agent/meta',
        'emulsion/agent/core',
        'emulsion/agent/exceptions',
        'emulsion/agent/action',
        'emulsion/agent/comparts',
        'emulsion/agent/process',
        'emulsion/agent/atoms',
        'emulsion/agent/views',
        'emulsion/agent/managers',
        'emulsion/tools/__init__',
        'emulsion/tools/calendar',
        'emulsion/tools/functions',
        'emulsion/tools/misc',
        'emulsion/tools/graph',
        'emulsion/tools/parallel',
        'emulsion/tools/parser',
        'emulsion/tools/plot',
        'emulsion/tools/simulation',
        'emulsion/tools/state',
        'emulsion/tools/timing',
        'emulsion/tools/view',
        'emulsion/tools/wind',
        'emulsion/environment/field',
        'emulsion/environment/__init__',
        'emulsion/environment/classes',
        'emulsion/templates/__init__',
        'emulsion/templates/specific_code',
        'emulsion/examples/quickstart',
    ],
    # packages=find_packages(where='src',
    #                        include=['*.py'],
    #                        exclude=['emulsion.dynpop']),
    package_dir = {'': 'src'},
    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'numpy>=1.13',             # BSD
        'scipy>=1.0',              # BSD
        'matplotlib>=2.1.1',       # Python Software Foundation
        'sympy>=1.1.1',            # BSD
        'pandas>=0.22',            # Simplified BSD
        'cython>=0.27',            # Apache
        'sqlalchemy>=1.1.13',      # MIT
        'sortedcontainers>=1.5.7', # Apache
        'progressbar2>=3.34',      # BSD
        'pyyaml>=3.12',            # MIT
        'docopt>=0.6.2',           # MIT
        'jinja2>=2.10',            # BSD
        'textX>=1.6',              # MIT
        'utm>=0.4',                # MIT
        'jupyter',                 # Modified (3-clause) BSD
        'ggplot',                  # BSD 2-Clause "Simplified" License
        # 'seaborn',                 # BSD 3-Clause
        # 'altair',                  # BSD 3-Clause
        # 'bokeh',                   # BSD 3-Clause
    ],
    python_requires='>=3.6',
    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install sampleproject[dev]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    extras_require={  # Optional
        'doc': [
            'doxypypy',              # GPL2
        ],
        'dev': [
            'setuptools>=38.5',      # MIT
            'pylint>=1.8.2',         # GPL
            # 'graphviz>=0.8.2',       # BSD
            # 'graphviz-python>=2.32', # Eclipse Public License
            # 'networkx>=2.1',         # BSD
        ],
    },

    include_package_data=True,
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # For example, the following would provide a command called `emulsion` which
    # executes the function `main` from this package when invoked:
    entry_points={  # Optional
        'console_scripts': [
            'emulsion = emulsion.__main__:main',
        ],
    },
    # List additional URLs that are relevant to your project as a dict.
    #
    # This field corresponds to the "Project-URL" metadata fields:
    # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    #
    # Examples listed include a pattern for specifying where the package tracks
    # issues, where the source is hosted, where to say thanks to the package
    # maintainers, and where to support the project financially. The key is
    # what's used to render the link text on PyPI.
    # project_urls={  # Optional
    #     'Bug Reports': 'https://github.com/pypa/sampleproject/issues',
    #     'Funding': 'https://donate.pypi.org',
    #     'Say Thanks!': 'http://saythanks.io/to/example',
    #     'Source': 'https://github.com/pypa/sampleproject/',
    # },
)
