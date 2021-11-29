from setuptools import setup, Extension

with open('README.md') as fh:
    long_description = fh.read()

setup(
    name='cyprimes',
    version='0.7.5',
    author='Andreas Suhre',
    author_email='andreas19@posteo.eu',
    url='https://github.com/andreas19/cyprimes/',
    description='Module for working with prime numbers.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['prime numbers'],
    license='BSD-3-Clause',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Cython',
        'Topic :: Software Development :: Libraries',
    ],
    ext_modules=[Extension('cyprimes', ['src/cyprimes.c'])],
    python_requires='>=3.7'
)
