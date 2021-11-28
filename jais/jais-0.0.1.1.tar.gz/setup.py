from setuptools import setup, find_packages
from jais.utils import load_default_configs

CNF = load_default_configs()

VERSION = '0.0.1.1'

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()


    
def read_requirements(path):
    with open(path) as f:
        req_list = f.read().split('\n')
    return [l.strip() for l in req_list]

setup(
    name="jais",
    version=VERSION,
    description='Just Artificial Inteliigence Snippets (JAIS)',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Jitender Singh Virk',
    author_email='krivsj@gmail.com',
    url='https://virksaab.github.io',
    # license='unlicensed',
    packages=find_packages(exclude=['ez_setup', 'tests*', ".github"]),
    # package_data={'myproject': ['templates/*']}, ?? WHAT IS THIS FOR?
    include_package_data=True,
    install_requires=read_requirements("requirements.txt"),
    entry_points=f"""
        [console_scripts]
        jais=jais.__main__:cli
    """,
)
