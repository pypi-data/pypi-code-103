import logging
import sys

import typer

from curvenote.models import (
    ArticleVersionPost,
    BlockChild,
    BlockKind,
    BlockPost,
    ContentVersionPost,
)

from ..client import Session

logger = logging.getLogger()


def clone_content(
    project: str = typer.Argument(
        ...,
        help=(
            "Identifier of existing Project containing ARTICLE. PROJECT may match title,"
            " name, or id of an existing Project. If no existing Project is found, an "
            "error will be raised"
        ),
    ),
    article: str = typer.Argument(
        ...,
        help=(
            "Identifier of existing Article. ARTICLE may match title, name, or id "
            "of an existing Article. If no existing Article is found, an error will"
            "be raised."
        ),
    ),
    new_article_name: str = typer.Argument(
        ...,
        help=(
            "Title of the new article to be created with cloned content."
            "If an article with the same name is found, an error will be raised."
        ),
    ),
    token: str = typer.Argument(
        ..., envvar="CURVENOTE_TOKEN", help="API token generated from curvenote.com"
    ),
    version: int = typer.Option(
        None,
        help=(
            "Version of the article to pull, if not specified will pull the latest version."
        ),
    ),
):
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    session = Session(token)

    typer.echo("Checking for project access")
    try:
        project_obj = session.get_project(project)
    except ValueError as err:
        typer.echo(f"Unable to access project {project}")
        typer.Exit(code=1)

    typer.echo("Fetching existing article block")
    try:
        block = session.get_block(project_obj, article, BlockKind.article)
    except ValueError as err:
        typer.echo(f"Unable to access article {article}")
        typer.Exit(code=1)

    version = int(version) if version is not None else block.latest_version
    typer.echo("Fetching existing article version")
    try:
        version = session.get_version(block, version)
    except ValueError as err:
        typer.echo(f"Unable to get article version {version}")
        typer.echo(str(err))
        typer.Exit(code=1)

    new_order = []
    new_children = {}

    for o in version.order:
        child = version.children[o]
        try:
            child_block = session.get_block(project_obj, child.src.block)
        except ValueError as err:
            typer.echo(f"Unable to access child, skipping {child.src}")
            continue

        if child_block.kind != BlockKind.content:
            typer.echo(f"Found {child_block.kind} block, referencing")
            new_order.append(child.id)
            new_children[child.id] = child
        else:
            typer.echo("Found content block, cloning")
            child_version = session.get_version(child_block, child.src.version)
            new_child_block = session.upload_block(
                BlockPost(kind=child_block.kind), project=project_obj
            )
            new_child_version = session.upload_version(
                version=ContentVersionPost(content=child_version.content),
                block=new_child_block,
            )
            new_order.append(child.id)
            new_children[child.id] = BlockChild(id=child.id, src=new_child_version.id)

    typer.echo(f"Existing article had {len(version.order)} children")
    typer.echo(f"Cloned article will have {len(new_order)} children")

    typer.echo(f"Creating new article")
    try:
        new_article_block = session.upload_block(
            BlockPost(name=new_article_name, kind=BlockKind.article),
            project=project_obj,
        )
    except ValueError as err:
        typer.echo("Could not create new article block")
        typer.echo(str(err))
        typer.Exit(code=1)

    try:
        session.upload_version(
            version=ArticleVersionPost(
                order=new_order,
                children=new_children,
                title=new_article_name,
            ),
            block=new_article_block,
        )
    except ValueError as err:
        typer.echo("Could not create new article version")
        typer.echo(str(err))
        typer.Exit(code=1)

    typer.echo(f"New article created: {new_article_name}")
