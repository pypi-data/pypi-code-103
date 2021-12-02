from setuptools import setup, find_packages

VERSION = '0.0.3'
DESCRIPTION = 'A general purpose with a wide range of features'
LONG_DESCRIPTION = 'A package with cryptography,audio playback,thread workers and a command line application framework'

# Setting up
setup(
    name="zono",
    version=VERSION,
    author="KisAwesome",
    author_email="cool676rock@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['colorama', 'cryptography', 'mutagen', 'python_vlc'],
    keywords=['python', 'Cryptography', 'vlc', 'audio',
              'songs', 'cli', 'framework', 'thread pools'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
