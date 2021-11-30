# Copyright (c) 2021 Mark Crowe <https://github.com/markcrowe-com>. All rights reserved.

from IPython.core.display import display, HTML


def create_jupyter_notebook_header(github_username: str, repository: str, notebook_filepath: str, branch: str = 'master', style: str = 'style="margin: auto;"') -> str:
    """
    Create an edit online header for Jupyter Notebook.
    :param github_username: GitHub username
    :param repository: repository name
    :param notebook_filepath: notebook filepath
    :param branch: branch name
    :return: HTML header
    """
    binder_url = f'https://mybinder.org/v2/gh/{github_username}/{repository}/{branch}?filepath={notebook_filepath}'
    colab_url = f'https://colab.research.google.com/github/{github_username}/{repository}/blob/{branch}/{notebook_filepath}'
    return f'<table {style}><tr><td><a href="{binder_url}" target="_parent"><img src="https://mybinder.org/badge_logo.svg" alt="Open In Binder"/></a></td><td>online editors</td><td><a href="{colab_url}" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a></td></tr></table>'


def display_jupyter_notebook_data_sources(datasource_filenames: list) -> None:
    """
    Print Data Sources for this notebook.
    :param repository_url: GitHub repository URL
    :param datasource_filenames: list of Data Source filenames
    """
    display(HTML('<strong>Data Sources</strong>'))
    display(HTML('<p>Data Sources available at</p>'))
    for datasource_filename in datasource_filenames:
        print(datasource_filename)


def display_jupyter_notebook_header(github_username: str, repository: str, notebook_filepath: str, branch: str = 'master') -> None:
    """
    Display an edit online header for Jupyter Notebook
    :param github_username: GitHub username
    :param repository: repository name
    :param notebook_filepath: notebook filepath
    :param branch: branch name
    """
    display(HTML(create_jupyter_notebook_header(
        github_username, repository, notebook_filepath, branch)))


def get_github_url(repository_url: str, filename: str) -> str:
    """
    Get GitHub URL
    :param repository_url: GitHub repository URL
    :param filename: filename
    :return: GitHub URL
    """
    return f'{repository_url}/{filename}'


def get_raw_github_url(repository_url: str, filename: str) -> str:
    """
    Get raw GitHub URL
    :param repository_url: GitHub repository URL
    :param filename: filename
    :return: raw GitHub URL
    """
    return get_github_url(repository_url, filename) + '?raw=true'


def print_jupyter_notebook_header_html(github_username: str, repository: str, notebook_filepath: str, branch: str = 'master') -> None:
    """
    print an edit online header for Jupyter Notebook
    :param github_username: GitHub username
    :param repository: repository name
    :param notebook_filepath: notebook filepath
    :param branch: branch name
    """
    print(create_jupyter_notebook_header(
        github_username, repository, notebook_filepath, branch))
