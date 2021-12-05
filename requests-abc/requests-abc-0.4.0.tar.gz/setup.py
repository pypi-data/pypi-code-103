from setuptools import setup, find_packages

setup(
    name='requests-abc',
    version='0.4.0',
    description='requests-abc',
    url='https://github.com/JustIceQAQ/Introspection/tree/main/code/requests_abc',
    author='justiceqaq',
    author_email='justiceqaq@gmail.com',
    license='MIT',
    zip_safe=False,
    packages=find_packages(),
    keywords=['requests-abc'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: Microsoft :: Windows :: Windows 10',

    ],
    install_requires=['requests'],
    python_requires=">=3.5"
)
