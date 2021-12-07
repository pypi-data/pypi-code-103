from setuptools import setup

VERSION = '1.0.0'
DESCRIPTION = 'Prints specified argument to console'
LONG_DESCRIPTION = 'Stupid package that makes ANOTHER function using the built it print function and is more slower and longer.'

setup(
    name="printIn",
    version=VERSION,
    author="DomIsAGamer",
    author_email="contact@domisagamer.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    keywords=['print', 'console'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.9",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)