import os
from setuptools import find_packages, setup


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

def read(filename):
    return open(filename, 'r', encoding='utf-8').read()

setup(
    name='django-firebase',
    version='0.0.7',
    packages=find_packages(),
    include_package_data=True,
    description='Django firebase support.',
    url='https://github.com/reOiL/django_firebase',
    author='Grigory Leikin (reOiL)',
    author_email='imidg3001@yandex.ru',
    zip_safe=False,
    license='BSD 3-Clause License',
    platforms=['any'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
    ],
    python_requires=">=3.5",
    install_requires=[
        'django>=2.0',
        'firebase-admin>=5.0.0'
    ],
)