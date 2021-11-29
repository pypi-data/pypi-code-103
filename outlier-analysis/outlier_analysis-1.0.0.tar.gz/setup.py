from setuptools import setup, find_packages


with open('README.md','r') as fh:
    long_description = fh.read()

setup(
    name = 'outlier_analysis',
    version = '1.0.0',
    description = 'Automatically detect, remove, and retrieve outliers using Standard Deviation, DBSCAN and Local Outlier Factor',
    py_modules = ['outlier_analysis'],
    packages = find_packages(exclude=('tests')),
    package_dir = {'':'src'},
    classifiers = [
       'Development Status :: 4 - Beta',
       'Intended Audience :: Other Audience',
       'License :: OSI Approved :: MIT License',
       'Natural Language :: English',
       'Operating System :: OS Independent',
       'Programming Language :: Python :: 3 :: Only',
       'Programming Language :: Python :: 3.8',
       'Programming Language :: Python :: 3.9'
    ],
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    install_requires = [
        'pandas ~= 1.2.4',
        'numpy ~= 1.19.5',
        'sklearn ~= 0.0',
        'joblib ~= 1.0.1'
    ],
    author = 'Ben Fuqua',
    author_email = 'Benjamin.Fuqua@gmail.com',
    url = 'https://github.com/cmbfuqua/outlier_detection_drl'
)