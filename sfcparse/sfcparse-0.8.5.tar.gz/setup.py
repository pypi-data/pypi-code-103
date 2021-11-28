from setuptools import setup

# General Setup
PIP_NAME = 'sfcparse'
MODULES_INSTALLED = ['sfcparse']
VERSION = '0.8.5'
DESCRIPTION = 'Simple File Configuration Parse. Easily import/export data!'
CODE_AUTHOR = 'aaronater10'
AUTHOR_EMAIL = 'dev_admin@dunnts.com'
PROJECT_URL = 'https://github.com/aaronater10/sfcparse'

# Import README
with open('.\\README.md', 'r') as f:
    LONG_DESCRIPTION = f.read()

# Main Setup Params
setup(
    name=PIP_NAME,
    version=VERSION,
    url=PROJECT_URL,
    author=CODE_AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    py_modules=MODULES_INSTALLED,
    package_dir={'': 'src'},
    install_requires=[],
    keywords=['python', 'py', 'config', 'file', 'export', 'parse', 'text file', 'cfg', 'conf', 'save file', 'config file', 'sfcparse', 'aaronater10', 'db', 'database', 'simple', 'configuration', 'alternative', 'safe', 'ini', 'json', 'xml', 'yml', 'data', 'import'],
    license = 'MIT',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)