from setuptools import setup, find_packages
import versioneer

setup(
    name='tsdataformat',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Chris T. Berthiaume',
    author_email='chrisbee@uw.edu',
    license='MIT',
    description='A Python project to manage time series data',
    long_description=open('README.rst', 'r').read(),
    url='https://github.com/ctberthiaume/tsdataformat-python',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only'
    ],
    keywords = ['csv', 'command-line', 'time series', 'tsdata'],
    python_requires='>=3.7, <4',
    install_requires=[
        'ciso8601',
        'click',
        'pandas'
    ],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'tsdataformat=tsdataformat.cli:cli'
        ]
    }
)
