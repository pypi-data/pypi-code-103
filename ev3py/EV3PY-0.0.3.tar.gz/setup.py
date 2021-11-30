from setuptools import find_packages, setup



setup(
    name="EV3PY",
    packages=find_packages(include=['EV3PY']),
    version="0.0.3",
    description="Convert Python Code to EV3 Code",
    long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
    author="Fynn Krebser",
    author_email= "fynn.krebser@gmail.com",
    license="MIT",
    keywords='EV3',
    install_requires=['']
)