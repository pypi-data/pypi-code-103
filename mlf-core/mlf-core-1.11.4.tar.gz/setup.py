# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mlf_core',
 'mlf_core.bump_version',
 'mlf_core.common',
 'mlf_core.config',
 'mlf_core.create',
 'mlf_core.create.domains',
 'mlf_core.create.templates.common_all_files.{{cookiecutter.common_all}}.docs',
 'mlf_core.create.templates.common_mlflow_files.{{ cookiecutter.common_mlflow '
 '}}.{{ cookiecutter.project_slug_no_hyphen }}.mlf_core',
 'mlf_core.create.templates.mlflow.mlflow_pytorch.{{ cookiecutter.project_slug '
 '}}.{{ cookiecutter.project_slug_no_hyphen }}',
 'mlf_core.create.templates.mlflow.mlflow_pytorch.{{ cookiecutter.project_slug '
 '}}.{{ cookiecutter.project_slug_no_hyphen }}.data_loading',
 'mlf_core.create.templates.mlflow.mlflow_pytorch.{{ cookiecutter.project_slug '
 '}}.{{ cookiecutter.project_slug_no_hyphen }}.model',
 'mlf_core.create.templates.mlflow.mlflow_tensorflow.{{ '
 'cookiecutter.project_slug }}.{{ cookiecutter.project_slug_no_hyphen }}',
 'mlf_core.create.templates.mlflow.mlflow_tensorflow.{{ '
 'cookiecutter.project_slug }}.{{ cookiecutter.project_slug_no_hyphen '
 '}}.data_loading',
 'mlf_core.create.templates.mlflow.mlflow_tensorflow.{{ '
 'cookiecutter.project_slug }}.{{ cookiecutter.project_slug_no_hyphen }}.model',
 'mlf_core.create.templates.mlflow.mlflow_tensorflow.{{ '
 'cookiecutter.project_slug }}.{{ cookiecutter.project_slug_no_hyphen '
 '}}.training',
 'mlf_core.create.templates.mlflow.mlflow_xgboost.{{ cookiecutter.project_slug '
 '}}.{{ cookiecutter.project_slug_no_hyphen }}',
 'mlf_core.create.templates.mlflow.mlflow_xgboost.{{ cookiecutter.project_slug '
 '}}.{{ cookiecutter.project_slug_no_hyphen }}.data_loading',
 'mlf_core.create.templates.package.package_prediction.hooks',
 'mlf_core.create.templates.package.package_prediction.{{ '
 'cookiecutter.project_slug_no_hyphen }}',
 'mlf_core.create.templates.package.package_prediction.{{ '
 'cookiecutter.project_slug_no_hyphen '
 '}}.{{cookiecutter.project_slug_no_hyphen}}',
 'mlf_core.custom_cli',
 'mlf_core.info',
 'mlf_core.lint',
 'mlf_core.lint.domains',
 'mlf_core.list',
 'mlf_core.sync',
 'mlf_core.upgrade',
 'mlf_core.util']

package_data = \
{'': ['*'],
 'mlf_core.create': ['templates/*',
                     'templates/common_all_files/*',
                     'templates/common_all_files/{{cookiecutter.common_all}}/*',
                     'templates/common_all_files/{{cookiecutter.common_all}}/.github/*',
                     'templates/common_all_files/{{cookiecutter.common_all}}/.github/ISSUE_TEMPLATE/*',
                     'templates/common_all_files/{{cookiecutter.common_all}}/.github/workflows/*',
                     'templates/common_mlflow_files/*',
                     'templates/common_mlflow_files/{{ '
                     'cookiecutter.common_mlflow }}/*',
                     'templates/common_mlflow_files/{{ '
                     'cookiecutter.common_mlflow }}/.github/workflows/*',
                     'templates/mlflow/mlflow_pytorch/*',
                     'templates/mlflow/mlflow_pytorch/{{ '
                     'cookiecutter.project_slug }}/*',
                     'templates/mlflow/mlflow_pytorch/{{ '
                     'cookiecutter.project_slug }}/docs/*',
                     'templates/mlflow/mlflow_tensorflow/*',
                     'templates/mlflow/mlflow_tensorflow/{{ '
                     'cookiecutter.project_slug }}/*',
                     'templates/mlflow/mlflow_tensorflow/{{ '
                     'cookiecutter.project_slug }}/docs/*',
                     'templates/mlflow/mlflow_xgboost/*',
                     'templates/mlflow/mlflow_xgboost/{{ '
                     'cookiecutter.project_slug }}/*',
                     'templates/mlflow/mlflow_xgboost/{{ '
                     'cookiecutter.project_slug }}/docs/*',
                     'templates/package/package_prediction/*'],
 'mlf_core.create.templates.common_all_files.{{cookiecutter.common_all}}.docs': ['_static/*'],
 'mlf_core.create.templates.package.package_prediction.{{ cookiecutter.project_slug_no_hyphen }}': ['.github/*',
                                                                                                    '.github/workflows/*',
                                                                                                    'docs/*',
                                                                                                    'makefiles/*'],
 'mlf_core.create.templates.package.package_prediction.{{ cookiecutter.project_slug_no_hyphen }}.{{cookiecutter.project_slug_no_hyphen}}': ['data/*',
                                                                                                                                            'models/*']}

install_requires = \
['GitPython>=3.1.15,<4.0.0',
 'Jinja2>=2.11.3,<4.0.0',
 'PyGithub>=1.54.1,<2.0.0',
 'PyNaCl>=1.4.0,<2.0.0',
 'PyYAML>=5.4.1,<7.0.0',
 'appdirs>=1.4.4,<2.0.0',
 'autopep8>=1.5.6,<2.0.0',
 'cffi>=1.14.5,<2.0.0',
 'click>=7.1.2,<9.0.0',
 'cookiecutter>=1.7.2,<2.0.0',
 'cryptography>=3.4.7,<36.0.0',
 'mlflow>=1.15.0,<2.0.0',
 'packaging>=20.9,<22.0',
 'questionary>=1.9.0,<2.0.0',
 'requests>=2.25.1,<3.0.0',
 'rich>=10.1.0,<11.0.0',
 'ruamel.yaml>=0.17.4,<0.18.0']

entry_points = \
{'console_scripts': ['mlf-core = mlf_core.__main__:main']}

setup_kwargs = {
    'name': 'mlf-core',
    'version': '1.11.4',
    'description': 'Reproducible machine learning pipelines using mlflow.',
    'long_description': ".. image:: https://user-images.githubusercontent.com/21954664/84388841-84b4cc80-abf5-11ea-83f3-b8ce8de36e25.png\n    :target: https://mlf-core.com\n    :alt: mlf-core logo\n\n|\n\n========\nmlf-core\n========\n\n|PyPI| |Python Version| |License| |Read the Docs| |Build| |Tests| |Codecov| |pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/mlf-core.svg\n   :target: https://pypi.org/project/mlf-core/\n   :alt: PyPI\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/mlf-core\n   :target: https://pypi.org/project/mlf-core\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/github/license/mlf-core/mlf-core\n   :target: https://opensource.org/licenses/Apache-2.0\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/mlf-core/latest.svg?label=Read%20the%20Docs\n   :target: https://mlf-core.readthedocs.io/\n   :alt: Read the documentation at https://mlf-core.readthedocs.io/\n.. |Build| image:: https://github.com/mlf-core/mlf-core/workflows/Build%20mlf-core%20Package/badge.svg\n   :target: https://github.com/mlf-core/mlf-core/actions?workflow=Package\n   :alt: Build Package Status\n.. |Tests| image:: https://github.com/mlf-core/mlf-core/workflows/Run%20mlf-core%20Tests/badge.svg\n   :target: https://github.com/mlf-core/mlf-core/actions?workflow=Tests\n   :alt: Run Tests Status\n.. |Codecov| image:: https://codecov.io/gh/mlf-core/mlf-core/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/mlf-core/mlf-core\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n.. image:: https://static.pepy.tech/personalized-badge/mlf-core?units=international_system&left_color=grey&right_color=green&left_text=Downloads\n   :target: https://pepy.tech/project/mlf-core\n   :alt: Pepy Downloads\n\n.. image:: https://img.shields.io/discord/742367395196305489?color=passing\n   :target: https://discord.gg/Mv8sAcq\n   :alt: Discord\n\nPreprint\n--------\n\n`mlf-core: a framework for deterministic machine learning <https://arxiv.org/abs/2104.07651>`_\n\n\nOverview\n--------\n\n.. figure:: https://user-images.githubusercontent.com/31141763/110704981-02921c80-81f6-11eb-8775-bd73f565568c.png\n   :alt: mlf-core overview\n\n   mlf-core provides CPU and GPU deterministic machine learning templates based on MLflow, Conda, Docker and a strong Github integration.\n   Templates are available for PyTorch, TensorFlow and XGBoost.\n   A custom linter ensures that projects stay deterministic in all phases of development and deployment.\n\nInstalling\n---------------\n\nStart your journey with mlf-core by installing it via ``$ pip install mlf-core``.\n\nSee `Installation  <https://mlf_core.readthedocs.io/en/latest/readme.html#installing>`_.\n\nrun\n----\nSee a mlf-core project in action.\n\n.. figure:: https://user-images.githubusercontent.com/31141763/117714817-c409e580-b1d7-11eb-9991-cb6eb58efbb7.gif\n\n\nconfig\n------\nConfigure mlf-core to get started.\n\n.. figure:: https://user-images.githubusercontent.com/31141763/102669098-f6199d00-418d-11eb-9ae6-26c12d9c1231.gif\n\nSee `Configuring mlf-core <https://mlf_core.readthedocs.io/en/latest/config.html>`_\n\nlist\n----\nList all available mlf-core templates.\n\n.. figure:: https://user-images.githubusercontent.com/31141763/102668939-8d322500-418d-11eb-8b2c-acd895fc50e3.gif\n\nSee `Listing all templates <https://mlf_core.readthedocs.io/en/latest/list_info.html#list>`_.\n\ninfo\n----\nGet detailed information on a mlf-core template.\n\n.. figure:: https://user-images.githubusercontent.com/31141763/102669191-324cfd80-418e-11eb-9542-d2995b7318a9.gif\n\nSee `Get detailed template information <https://mlf_core.readthedocs.io/en/latest/list_info.html#info>`_.\n\ncreate\n------\nKickstart your deterministic machine laerning project with one of mlf-core's templates in no time.\n\n.. figure:: https://user-images.githubusercontent.com/31141763/102669143-1184a800-418e-11eb-853b-0deb0387efc6.gif\n\nSee `Create a project <https://mlf_core.readthedocs.io/en/latest/create.html>`_.\n\nlint\n----\nUse advanced linting to ensure your project always adheres to mlf-core's standards and stays deterministic.\n\n.. image:: https://user-images.githubusercontent.com/31141763/102668893-696edf00-418d-11eb-888e-822244a6f5dc.gif\n\nSee `Linting your project <https://mlf_core.readthedocs.io/en/latest/lint.html>`_\n\nbump-version\n------------\nBump your project version across several files.\n\n.. figure:: https://user-images.githubusercontent.com/31141763/102668987-aaff8a00-418d-11eb-9292-dc512f77f09b.gif\n\nSee `Bumping the version of an existing project  <https://mlf_core.readthedocs.io/en/latest/bump_version.html>`_.\n\nsync\n------\nSync your project with the latest mlf-core release to get the latest template features.\n\n.. figure:: https://user-images.githubusercontent.com/31141763/102669065-de421900-418d-11eb-9e1b-a76487d02b2a.gif\n\nSee `Syncing a project <https://mlf_core.readthedocs.io/en/latest/sync.html>`_.\n\nupgrade\n-------\nCheck whether you are using the latest mlf-core version and update automatically to benefit from the latest features.\n\nSee `<https://mlf_core.readthedocs.io/en/latest/upgrade.html>`_.\n\n\nCredits\n-------\n\nPrimary idea and main development by `Lukas Heumos <https://github.com/zethson/>`_. mlf-core is inspired by nf-core_.\nThis package was created with cookietemple_ based on a modified `audreyr/cookiecutter-pypackage`_ project template using cookiecutter_.\n\n.. _MLflow: https://mlflow.org\n.. _cookietemple: https://cookietemple.com\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _MIT: http://opensource.org/licenses/MIT\n.. _PyPI: https://pypi.org/\n.. _Hypermodern_Python_Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _pip: https://pip.pypa.io/\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Usage: https://mlf-core.readthedocs.io/en/latest/usage.html\n.. _cookiecutter: https://github.com/audreyr/cookiecutter\n.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage\n.. _nf-core: https://nf-co.re\n",
    'author': 'Lukas Heumos',
    'author_email': 'lukas.heumos@posteo.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mlf-core/mlf-core',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<3.10',
}


setup(**setup_kwargs)
