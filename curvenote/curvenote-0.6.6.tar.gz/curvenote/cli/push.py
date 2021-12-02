import logging
import os
import subprocess
import sys

import typer

from ..client import Session

logger = logging.getLogger()


def push(
    path: str = typer.Argument(..., help="Local file or folder to push to curvenote."),
    project: str = typer.Argument(
        ...,
        help=(
            "Identifier of target Project. PROJECT may match title, name, or id "
            "of an existing Project. If no existing Project is found, a new "
            "Project will be created with title PROJECT."
        ),
    ),
    article: str = typer.Option(
        None,
        help=(
            "Identifier of target Article. ARTICLE may match title, name, or id "
            "of an existing Article. If no existing Article is found, a new "
            "Article will be created with title ARTICLE. ARTICLE is ignored if "
            "PATH is a folder. If PATH is a folder or ARTICLE is not provided, "
            "filename will be used for Article."
        ),
    ),
    team: str = typer.Option(
        None,
        help=(
            "Team to use when creating a new Project. TEAM is ignored if PROJECT "
            "already exists. If PROJECT does not exist and TEAM is not provided, "
            "the new Project will be created under the current user."
        ),
    ),
    token: str = typer.Argument(
        ..., envvar="CURVENOTE_TOKEN", help="API token generated from curvenote.com"
    ),
):
    """Push contents of local file or folder to curvenote Project"""
    if not os.path.exists(path):
        raise ValueError(f"path not found: {path}")
    session = Session(token)

    typer.echo("Checking for project access")
    project_obj = session.get_or_create_project(
        title=project,
        team=team,
    )
    if os.path.isdir(path):
        typer.echo("pushing from folder")
        session.documents_from_folder(folder=path, project=project_obj)
    elif os.path.isfile(path):
        _, file_extension = os.path.splitext(path)
        if file_extension == ".ipynb":
            typer.echo("pushing notebook file...")
            session.notebook_from_file(
                filename=path, project=project_obj, title=article
            )
        elif file_extension == ".md":
            typer.echo("pushing markdown file...")
            session.article_from_file(filename=path, project=project_obj, title=article)
        else:
            raise ValueError(f"unsupported file type: {file_extension}")
    else:
        raise ValueError(f"unable to resolve path: {path}")
