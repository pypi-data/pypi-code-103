from setuptools import setup
import re


VERSIONFILE="QuarchpyQCS/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(name='quarchQCS',
      version=verstr,
      description='This packpage contains the Quarch Compliance suite server',
      # home_page = 'https://www.quarch.com',
      author='Quarch Technology ltd',
      author_email='support@quarch.com',
      license='Quarch Technology ltd',
      keywords='quarch quarchpy QCS torridon',
      packages=['QuarchpyQCS',
      'quarchpyQCS.certs',
      'quarchpyQCS.Docs',
      'quarchpyQCS.pciutils'],
      classifiers=
      [
      'Intended Audience :: Information Technology',
      'Intended Audience :: Developers',
      'Natural Language :: English',
      'Operating System :: MacOS',
      'Operating System :: Microsoft :: Windows',
      'Operating System :: POSIX',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Information Analysis',
      'Topic :: System',
      'Topic :: System :: Power (UPS)'
      ],
      install_requires=[
          'quarchpy>=2.0.22.dev2',
          'numpy',
          'pandas'],
      include_package_data=True,
      zip_safe=False)