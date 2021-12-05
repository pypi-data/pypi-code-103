from setuptools import setup

setup(
    name='expressmoney',
    packages=('expressmoney',),
    version='0.0.1',
    description='SDK ExpressMoney',
    long_description='Software development kit ExpressMoney company',
    long_description_content_type="text/markdown",
    author='Sergey Zherebtsov',
    author_email='sergey@expressmoney.com',
    url='https://github.com/zsergey85/',
    install_requires=('google-cloud-pubsub', 'google-cloud-tasks', 'google-cloud-storage'),
    download_url='https://github.com/zsergey85/',
    keywords=('expressmoney',),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    python_requires='>=3.7',
)
