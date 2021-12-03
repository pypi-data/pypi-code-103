from setuptools import find_packages,setup
from xes import version
import sys
if __name__=="__main__":
  sys.argv.append('sdist')
setup(
    name = 'py process bar'.replace(" ",''),
    version = version.version,
    author = 'Ruoyu Wang',
    description = '进度显示库',
    packages = find_packages(),
    install_requires = ["requests", "xes-lib", "urllib"],
    url = 'https://code.xueersi.com'
)