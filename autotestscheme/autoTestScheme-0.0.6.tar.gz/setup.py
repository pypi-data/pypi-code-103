import sys

from setuptools import setup, find_packages

packages = find_packages("src")

setup(name='autoTestScheme',
      version='0.0.6',
      url='https://gitee.com/xiongrun/auto-test-scheme',
      author='wuxing',
      description='auto test scheme',
      long_description='file: README.md',
      long_description_content_type='text/markdown',
      author_email='xr18668178362@163.com',
      project_urls={'Bug Tracker': 'https://gitee.com/xiongrun/auto-test-scheme/issues'},
      package_dir={'': 'src'},
      packages=packages,
      include_package_data=True,
      entry_points={'pytest11': ['pytest_autoTestScheme = autoTestScheme']},
      package_data={
          'demo': ['demo/*'],
          'autoTestScheme': ['allure/*'],
      },
      )
