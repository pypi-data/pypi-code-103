from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='colego',
    version='0.0.1',
    description='Simple package that converts a text to have colors in a terminal output.',
    long_description=open('README.txt').read() + '\n\n' + "Change Log\n==========\n\n0.0.1 (2021-12-05)\n------------------\n- First Release",
    url='',
    author="Hastaluego",
    author_email="superduperst3ve@gmail.com",
    license="MIT",
    classifiers=classifiers,
    keywords=["color", "colour", "terminal", "output", "text", "colored", "coloured"],
    packages=find_packages(),
    install_requires=['']
)