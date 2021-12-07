from setuptools import find_packages, setup

setup(
    name='django_generic_json_class_based_views',
    packages=find_packages(include=['django_generic_json_views']),
    version='0.6.0',
    license='MIT',
    description='Generic JSON class based views for the webframework Django.',
    author='Timo Michel',
    author_email='TimoM96@outlook.de',
    url='https://github.com/T1mbo96/django_generic_json_views',
    download_url='https://github.com/T1mbo96/django_generic_json_views/archive/refs/tags/v_060.tar.gz',
    keywords=['django', 'json'],
    install_requires=['Django>=2.2'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==6.2.5'],
    test_suite='tests',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ]
)