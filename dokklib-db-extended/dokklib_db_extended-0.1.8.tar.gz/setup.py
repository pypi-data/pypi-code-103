from setuptools import find_packages, setup

with open('README.md') as f:
    long_description = f.read()
import dokklib_db_extended
def local_scheme(version):
    return ""
setup(
    name='dokklib_db_extended',
    version='0.1.8',
    author='Agost Biro, Cristian Dominguez',
    author_email='agost+dokklib_db_extended@dokknet.com, crisdomgo@gmail.com',
    description='DynamoDB Single Table Library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cdominguezg/dokklib-db-extended',
    download_url='https://github.com/cdominguezg/dokklib-db-extended/archive/v0.1.8.tar.gz',
    packages=find_packages(exclude=['tests*']),
    use_scm_version=False,
    # Needed to let mypy use package for type hints
    zip_safe=False,
    package_data={"dokklib_db_extended": ["py.typed"]},
    setup_requires=['setuptools_scm'],
    python_requires='>=3.6',
    include_package_data=True,
    install_requires=[
        'typing-extensions>=3.7.2,<4',
        'boto3'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Database'
    ]
)
