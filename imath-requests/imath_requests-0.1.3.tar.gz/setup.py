import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='imath_requests',
    author='Industrial 3D Robotics',
    author_email='bknight@i3drobotics.com',
    description='Communication with the iMath data platform REST API',
    keywords='imath, i3dr, stereo, requests',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/i3drobotics/imath_requests',
    project_urls={
        'Documentation': 'https://github.com/i3drobotics/imath_requests',
        'Bug Reports':
        'https://github.com/i3drobotics/imath_requests/issues',
        'Source Code': 'https://github.com/i3drobotics/imath_requests',
    },
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        # see https://pypi.org/classifiers/
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    # install_requires=['Pillow'],
    extras_require={
        'dev': ['check-manifest'],
        # 'test': ['coverage'],
    },
    # entry_points={
    #     'console_scripts': [  # This can provide executable scripts
    #         'run=examplepy:main',
    # You can execute `run` in bash to run `main()` in src/examplepy/__init__.py
    #     ],
    # },
)
