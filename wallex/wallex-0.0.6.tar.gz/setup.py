from distutils.core import setup

setup(
    name='wallex',
    packages=['wallex'],
    version='0.0.6',
    license='MIT',
    description='Wallex cryptocurrency exchange python sdk',
    author='amiwrpremium',
    author_email='amiwrpremium@gmail.com',
    url='https://github.com/amiwrpremium/wallex',
    keywords=['wallex', 'crypto', 'exchange', 'API', "SDK"],
    install_requires=[
        'requests',
        'simplejson',
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
