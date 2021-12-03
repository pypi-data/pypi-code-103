from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='ud2pos',
      version='0.114',
      description='Method to get part-of-speech tags from universal dependencies data.',
      long_description=readme(),
      keywords='part-of-speech universal-dependencies',
      url='https://github.com/tpimentelms/ud2pos',
      author='Tiago Pimentel',
      author_email='tpimentelms@gmail.com',
      license='MIT',
      packages=['ud2pos'],
      include_package_data=True,
      zip_safe=False)
