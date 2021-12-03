"""
USAGE: 
   o install in develop mode: navigate to the folder containing this file,
                              and type 'pip install -e .'.
                              (add '--user' if you do not use virtualenvs)                           
"""
from setuptools import setup
try:
    import readdy
except ModuleNotFoundError:
    msg = ("Can't import readdy. You need to install readdy before you can use "
           "the bead_state_model package. "
           "Follow the install instructions on https://readdy.github.io/index.html "
           "to create a conda environment with readdy installed, and then install "
           "bead_state_model into that conda environment.")
    raise ModuleNotFoundError(msg)

setup(name='bead_state_model',
      version='2.3.1',
      description='Wrapper for ReaDDy2 to set up simulations of actomyosin networks.',
      url='',
      author='Ilyas Kuhlemann',
      author_email='ilyasp.ku@gmail.com',
      license='GNU GPLv3',
      packages=["bead_state_model",
                "bead_state_model.network_assembly"],
      entry_points={
          "console_scripts": [
          ],
          "gui_scripts": [
          ]
      },
      install_requires=["numpy",
                        "pandas",
                        "toml>=0.10.2"],
      zip_safe=False)
