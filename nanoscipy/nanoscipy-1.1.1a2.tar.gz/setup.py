import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='nanoscipy',
    version='1.1.1a2',
    author='Nicholas Hansen',
    author_email='nicholas.2000@live.dk',
    description='A package containing costum compiled functions, to make data-handling and analysis easier.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/nicholas12392/nanoscipy',
    project_urls = {
        "Bug Tracker": "https://github.com/nicholas12392/nanoscipy/issues"
    },
    license='MIT',
    packages=['nanoscipy'],
    install_requires=['requests'],
)
