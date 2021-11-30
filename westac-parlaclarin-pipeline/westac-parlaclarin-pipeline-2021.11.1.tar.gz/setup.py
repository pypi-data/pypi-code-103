# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scripts', 'workflow', 'workflow.config', 'workflow.rules', 'workflow.taggers']

package_data = \
{'': ['*'], 'scripts': ['wip/*']}

install_requires = \
['click>=7.1.2,<8.0.0',
 'cookiecutter>=1.7.2,<2.0.0',
 'dehyphen>=0.3.4,<0.4.0',
 'loguru>=0.5.3,<0.6.0',
 'pandas>=1.2.3,<2.0.0',
 'pygit2>=1.5.0,<2.0.0',
 'pyriksprot>=2021.9.8,<2022.0.0',
 'snakefmt>=0.3.1,<0.4.0',
 'snakemake>=6.0.5,<7.0.0',
 'stanza>=1.2.3,<2.0.0',
 'transformers>=4.3.3,<5.0.0']

entry_points = \
{'console_scripts': ['config_value = scripts.config_value:main']}

setup_kwargs = {
    'name': 'westac-parlaclarin-pipeline',
    'version': '2021.11.1',
    'description': 'Pipeline that transforms Parla-Clarin XML files',
    'long_description': '# Riksdagens Protokoll Part-Of-Speech Tagging (Parla-Clarin Workflow)\n\nThis package implements Stanza part-of-speech annotation of `Riksdagens Protokoll` Parla-Clarin XML files.\n\n\n## Prerequisites\n\n- A bash-enabled environment (Linux or Git Bash on windows)\n- Git\n- Python 3.8.5^\n- GNU make (install i)\n\n# Parla-Clarin to penelope pipeline\n\n## How to install\n\n## How to configure\n\n## How to setup data\n\n### Riksdagens corpus\n\nCreate a shallow clone (no history) of repository:\n\n```bash\nmake init-repository\n```\n\nSync shallow clone with changes on origin (Github):\n\n```bash\nmake update-repositoryupdate_repository_timestamps\n```\n\nUpdate modified date of repository file. This is necessary since the pipeline uses last commit date of\neach XML-files to determine which files are outdated, whilst `git clone` sets current time.\n\n```bash\n$ make update-repository-timestamps\nor\n$ scripts/git_update_mtime.sh path-to-repository\n```\n\n## How to annotate speeches\n\n```bash\nmake annotate\nor\n$ nohup poetry run snakemake -j4 --keep-going --keep-target-files &\n```\n\nWindows:\n\n```bash\npoetry shell\nbash\nnohup poetry run snakemake -j4 -j4 --keep-going --keep-target-files &\n```\n\nRun a specific year:\n\n```bash\npoetry shell\nbash\nnohup poetry run snakemake --config -j4 --keep-going --keep-target-files &\n```\n## Install\n\n(This workflow will be simplified)\n\nVerify current Python version (`pyenv` is recommended for easy switch between versions).\n\nCreate a new Python virtual environment (sandbox):\n\n```bash\ncd /some/folder\nmkdir westac_parlaclarin_pipeline\ncd westac_parlaclarin_pipeline\npython -m venv .venv\nsource .venv/bin/activate\n```\n\nInstall the pipeline and run setup script.\n\n```bash\npip install westac_parlaclarin_pipeline\nsetup-pipeline\n```\n\n## Initialize local clone of Parla-CLARIN repository\n\n## Run PoS tagging\n\nMove to sandbox and activate virtual environment:\n\n```bash\ncd /some/folder/westac_parlaclarin_pipeline\nsource .venv/bin/activate\n```\n\nUpdate repository:\n\n```bash\nmake update-repository\nmake update-repository-timestamps\n```\n\nUpdate all (changed) annotations:\n\n```bash\nmake annotate\n```\n\nUpdate a single year (and set cpu count):\n\n```bash\nmake annotate YEAR=1960 CPU_COUNT=1\n```\n\n## Configuration\n\n\n```yaml\nwork_folders: !work_folders &work_folders\n  data_folder: /data/riksdagen_corpus_data\n\nparla_clarin: !parla_clarin &parla_clarin\n  repository_folder: /data/riksdagen_corpus_data/riksdagen-corpus\n  repository_url: https://github.com/welfare-state-analytics/riksdagen-corpus.git\n  repository_branch: dev\n  folder: /data/riksdagen_corpus_data/riksdagen-corpus/corpus\n\nextract_speeches: !extract_speeches &extract_speeches\n  folder: /data/riksdagen_corpus_data/riksdagen-corpus-exports/speech_xml\n  template: speeches.cdata.xml\n  extension: xml\n\nword_frequency: !word_frequency &word_frequency\n  <<: *work_folders\n  filename: riksdagen-corpus-term-frequencies.pkl\n\ndehyphen: !dehyphen &dehyphen\n  <<: *work_folders\n  whitelist_filename: dehyphen_whitelist.txt.gz\n  whitelist_log_filename: dehyphen_whitelist_log.pkl\n  unresolved_filename: dehyphen_unresolved.txt.gz\n\nconfig: !config\n    work_folders: *work_folders\n    parla_clarin: *parla_clarin\n    extract_speeches: *extract_speeches\n    word_frequency: *word_frequency\n    dehyphen: *dehyphen\n    annotated_folder: /data/riksdagen_corpus_data/annotated\n```\n',
    'author': 'Roger Mähler',
    'author_email': 'roger.mahler@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://westac.se',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '==3.8.5',
}


setup(**setup_kwargs)
