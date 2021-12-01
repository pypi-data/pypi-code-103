from codecs import open

from setuptools import find_packages, setup

import versioneer

with open('requirements.txt') as f:
    requirements = f.read().split()

git_requirements = [r for r in requirements if r.startswith('git+')]
requirements = [r for r in requirements if not r.startswith('git+')]
if len(git_requirements) > 0:
    print("User must install the following packages manually:\n" +
          "\n".join(f' {r}' for r in git_requirements))

setup(name='pvsim',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      license='Apache License 2.0',
      author='hhslepicka',
      install_requires=requirements,
      packages=find_packages(),
      description='Simulator of PVAccess PVs',
      long_description=open('README.md', 'r', encoding='utf-8').read(),
      long_description_content_type='text/markdown',
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'pvsim=pvsim.launcher:main'
          ]
      }
)
