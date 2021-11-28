from setuptools import setup, find_packages


with open('./requirements.txt', 'r') as reqs_file:
    reqs = reqs_file.readlines()


setup(
    name='helios-opentelemetry-sdk',
    version='0.1.3',
    description='Helios opentelemetry SDK',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Helios',
    author_email='support@gethelios.dev',
    url='https://github.com/heliosphere-io/python-sdk',
    packages=find_packages(exclude=["tests.*", "tests"]),
    install_requires=reqs,
    setup_requires=['pytest-runner', 'flake8'],
    tests_require=['pytest'],
    keywords=[
        'helios',
        'heliosphere',
        'microservices',
        'tracing',
        'distributed-tracing',
        'debugging',
        'testing'
    ],
    entry_points={"pytest11": ["name_of_plugin = hstest"]},
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Framework :: Pytest",
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
