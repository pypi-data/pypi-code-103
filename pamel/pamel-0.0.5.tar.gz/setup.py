from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='pamel',
      version='0.0.5',
      long_description=readme(),
      long_description_content_type='text/x-rst;',
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
      ],
      keywords='automl, credit',
      author='Rute Souza de Abreu',
      author_email='rute.s.abreu@gmail.com',
      license='MIT',
      packages=['paml'],
      install_requires=[
          'scikit-learn',
          'numpy',
          'Boruta',
          'pandas',
          'xgboost',
          'catboost',
          'lightgbm',
          'optuna'
      ],
      include_package_data=True,
      zip_safe=True)
