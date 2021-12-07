from setuptools import setup, find_packages

with open('README.md', 'r') as readme:
    long_description = readme.read()

# Also change version in kntgen/__init__.py

setup(
    name='kntgen',
    version='1.0.8',
    author='kiendtvt1411',
    author_email='dtvtdevelopersk58@gmail.com',
    description='A generator for Dart code using by Appixi\'s projects',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/appixi/knt_dart_generator',
    packages=find_packages(),
    entry_points='''
        [console_scripts]
        kntgen=kntgen.__main__:main
    ''',
    install_requires=[
        'arghandler>=1.2',
        'regex',
        'googletrans==4.0.0rc1',
        'requests',
        'pyyaml',
        'tqdm',
        'jinja2>=2.10',
        'pydantic',
        'sheetfu'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    include_package_data=True
)
