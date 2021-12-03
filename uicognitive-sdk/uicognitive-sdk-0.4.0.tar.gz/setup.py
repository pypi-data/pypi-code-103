from setuptools import setup
import sys
tag = '1.0'
if '--tag' in sys.argv:
    index = sys.argv.index('--tag')
    sys.argv.pop(index)  # Removes the '--foo'
    tag = sys.argv.pop(index)[1:]  # Returns the element after the '--foo'
setup(version=tag)