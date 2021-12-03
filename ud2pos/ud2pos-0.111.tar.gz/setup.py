from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='ud2pos',
      version='0.111',
      description='Method to get part-of-speech tags from universal dependencies data.',
      long_description=readme(),
      keywords='part-of-speech universal-dependencies',
      url='https://github.com/tpimentelms/ud2pos',
      author='Tiago Pimentel',
      author_email='tpimentelms@gmail.com',
      license='MIT',
      packages=['ud2pos'],
      # scripts=['ud2pos'],
      # entry_points={
      #     'console_scripts': [
      #         'nbne=nbne.get_embeddings:main',
      #     ],
      # },
      # install_requires=[
      #     'networkx',
      #     'gensim'
      # ],
      zip_safe=False)
