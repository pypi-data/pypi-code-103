import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

# This call to setup() does all the work
setuptools.setup(
    name='fad',
    version='0.0.3',
    author='Allan Wu',
    author_email='wuallanx@gmail.com',
    description='Download an album of photos from facebook',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/wuallanx/facebook-album-downloader',
    project_urls={
        'Bug Tracker': 'https://github.com/wuallanx/facebook-album-downloader/issues',
    },
    license='GNU GPLv3',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
    packages=setuptools.find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=['requests==2.26.0', 'selenium==4.0.0'],
    entry_points={
        'console_scripts': [
            'fad=fad.__main__:main',
        ],
    },
    python_requires='>=3.9',
)
