from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='ezdatabase',
    version='1.5',
    description='A simple database wrapper for Python 3',
    author='JJTV',
    long_description_content_type='text/markdown',
    long_description=open('README.md').read() + '\n\n\n\n' + open('CHANGELOG.txt').read(),
    url='',
    license='MIT',
    classifiers=classifiers,
    keywords=["database wrapper", "ezdatabase", "easydatabase", "easy database", "repl.it database", "sql alternative", "sqlite"],
    packages=["ezdatabase"],
    install_requires=[''],
    include_package_data=True
)