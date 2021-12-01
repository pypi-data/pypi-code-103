"""Packaging settings."""
import subprocess
from setuptools import find_packages, setup


def get_git_revision_short_hash() -> str:
    try:
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
    except:
        # if this is packaged up, then there is no git version (since its been packaged up and above will fail
        return "0.0.0"

try:
    with open('requirements.txt', 'r') as f:
        requirements = f.readlines()
except:
    # if this is packaged up, requirements.txt isn't present, its in the /tmp dir of the package
    with open('platform_services_lib.egg-info/requires.txt') as f:
        requirements = f.readlines()

setup(
    name='platform-services-lib',
    version=get_git_revision_short_hash(),
    python_requires='>3.6.0',
    url='https://ihsmarkit.com',
    description='Data Lake services lib.',
    author='IHS Markit Data Lake Team',
    author_email='datalake-support@ihsmarkit.com',
    license='MOZ-2',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='datalake, data, lake',
    packages=(find_packages(exclude=['docs', 'tests'])),
    install_requires=requirements
)
