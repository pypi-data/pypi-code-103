import os
import re
from setuptools import setup, find_packages

regexp = re.compile(r'.*__version__ = [\'\"](.*?)[\'\"]', re.S)

base_package = 'compu_methods'
base_path = os.path.dirname(__file__)

init_file = os.path.join(base_path, 'compu_methods', '__init__.py')
with open(init_file, 'r') as f:
    module_content = f.read()

    match = regexp.match(module_content)
    if match:
        version = match.group(1)
    else:
        raise RuntimeError(
            'Cannot find __version__ in {}'.format(init_file))

with open('README.rst', 'r') as f:
    readme = f.read()

with open('CHANGELOG.rst', 'r') as f:
    changes = f.read()

def parse_requirements(filename):
    ''' Load requirements from a pip requirements file '''
    with open(filename, 'r') as fd:
        lines = []
        for line in fd:
            line.strip()
            if line and not line.startswith("#"):
                lines.append(line)
    return lines

requirements = parse_requirements('requirements.txt')


if __name__ == '__main__':
    setup(
        name='compu_methods',
        description='ASAM, Autosar, MSRSW CompuMethods',
        long_description='\n\n'.join([readme, changes]),
        license='GNU General Public License v3',
        url='https://github.com/christoph2/compu-methods',
        version=version,
        author='Christoph Schueler',
        author_email='cpu12.gems@googlemail.com',
        maintainer='Christoph Schueler',
        maintainer_email='cpu12.gems@googlemail.com',
        install_requires=requirements,
        keywords=['compu_methods'],
        package_dir={'': 'compu_methods'},
        packages=find_packages('compu_methods'),
        zip_safe=False,
        classifiers=['Development Status :: 3 - Alpha',
                     'Intended Audience :: Developers',
                     "Topic :: Software Development",
                     "Topic :: Scientific/Engineering",
                     'Programming Language :: Python :: 3.6',
                     "Programming Language :: Python :: 3.7",
                     "Programming Language :: Python :: 3.8",
                     "Programming Language :: Python :: 3.9",
                     ]
    )
