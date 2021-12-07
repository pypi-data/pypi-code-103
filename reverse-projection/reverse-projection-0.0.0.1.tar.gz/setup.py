from setuptools import setup, find_packages

setup(
    name='reverse-projection',
    version='0.0.0.1',
    description=(
        'fast-machine-learning'
    ),
    author='luktian',
    author_email='luktian@shu.edu.cn',
    maintainer='luktian',
    maintainer_email='luktian@shu.edu.cn',
    license='BSD License',
    packages=find_packages(exclude=[
        "__pycache__"
        ]),
    data_files=[
        ],
    platforms=["windows"],
    python_requires=">=3.6",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'hyperopt',
        'numpy'
    ],
)