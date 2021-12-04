from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='nnfpy',
    version='1.0.1',
    description='Neural network on python',
    long_description=readme(),
    long_description_content_type="text/markdown",
    url='https://github.com/sopho-s/nnfpy',
    author='Nick Woods',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    author_email='woodsnicholas01@gmail.com',
    license='MIT',
    keywords='',
    packages=find_packages('src'),
    package_dir={'': 'src'}
)
