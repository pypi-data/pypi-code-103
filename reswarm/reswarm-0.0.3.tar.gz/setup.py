from setuptools import setup, find_packages

requirements = []
with open('requirements.txt', 'r') as fh:
    for line in fh:
        requirements.append(line.strip())

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='reswarm',
    version='0.0.3',
    description='Aids users in publishing data to a Record Evolution Datapod',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/RecordEvolution/reswarm-python',
    author='Record Evolution GmbH',
    author_email='marko.petzold@record-evolution.de',
    packages=find_packages(),
    license="MIT",
    python_requires=">=3.6",
    install_requires=requirements,
    classifiers=[]
)
