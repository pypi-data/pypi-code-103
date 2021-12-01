import versioneer
from setuptools import setup, find_packages


with open('requirements.txt') as f:
    REQUIREMENTS = f.read().splitlines()

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='drb-impl-xml',
    packages=find_packages(include=['drb_impl_xml']),
    description='DRB XML implementation',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='GAEL Systems',
    author_email='info@gael.fr',
    url='https://gitlab.com/drb-python/impl/xml',
    install_requires=REQUIREMENTS,
    setup_requires=['setuptools_scm'],
    test_suite='tests',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",

    ],
    python_requires='>=3.8',
    entry_points={'drb.impl': 'xml = drb_impl_xml.drb_impl_signature'},
    use_scm_version=True,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)
