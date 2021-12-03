import setuptools

setuptools.setup(
    name="convert2pyc",
    version="0.1",
    author="zxg",
    author_email="",
    description="convert py to pyc",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'convert2pyc=convert2pyc:main'
        ],
    },
)
