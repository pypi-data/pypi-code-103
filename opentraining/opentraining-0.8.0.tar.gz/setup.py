from setuptools import setup

setup(
    name='opentraining',
    version='0.8.0',
    description='A set of Sphinx extensions to manage training material',

    # long_description='blah',
    # long_description_content_type='text/markdown',

    url='https://faschingbauer.me',
    author='Jörg Faschingbauer',

    # https://pypi.org/classifiers/
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',
        # 'Intended Audience :: Developers',
        # 'Topic :: Software Development :: Build Tools',
        # 'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],

    keywords='homepage, training, opentraining',  # Optional
    package_dir = {'': 'src'},
    packages = [
        'opentraining',
        'opentraining.sphinxglue',
    ],
    python_requires='>=3.6, <4',
    install_requires=[
        'networkx',
        'Sphinx',
    ],
)
