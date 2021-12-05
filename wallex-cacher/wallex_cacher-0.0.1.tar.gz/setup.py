from distutils.core import setup

setup(
    name='wallex_cacher',
    packages=['wallex_cacher'],
    version='0.0.1',
    license='MIT',
    description='Wallex Orderbook Cacher',
    author='amiwrpremium',
    author_email='amiwrpremium@gmail.com',
    url='https://github.com/amiwrpremium/wallex_cacher',
    keywords=['wallex', 'crypto', 'exchange', 'API', "SDK", "Cacher"],
    install_requires=[
        'requests',
        'simplejson',
        'wallex',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
