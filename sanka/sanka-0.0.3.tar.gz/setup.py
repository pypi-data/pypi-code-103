from setuptools import setup


setup(
    name='sanka',
    description='a function decorator for surfacing dead code',
    use_scm_version=True,
    author='Emmanuel I. Obi',
    maintainer='Emmanuel I. Obi',
    maintainer_email='withtwoemms@gmail.com',
    url='https://github.com/withtwoemms/sanka',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    setup_requires=[
        'setuptools_scm==5.0.1'
    ],
)
