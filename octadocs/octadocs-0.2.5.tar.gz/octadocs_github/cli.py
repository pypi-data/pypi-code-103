import json
import logging
from pathlib import Path

from github import Github, UnknownObjectException
from rdflib import XSD
from typer import Typer
from urlpath import URL

from ldflex import LDFlex
from octadocs.storage import load_graph
from octadocs_github.models import RepoDescription

logger = logging.getLogger(__name__)
app = Typer(
    name='github',
    help='Manage data from GitHub.',
)


def ldflex_from_cache() -> LDFlex:
    graph = load_graph(Path.cwd() / '.cache/octadocs')
    return LDFlex(graph=graph)


def describe_repo(
    name: str,
    github_api_base_url: URL,
) -> RepoDescription:
    """
    Describe a repo by its full name.

    Full name format: {owner}/{repo}.
    """
    github = Github()
    repo = github.get_repo(name)
    raise ValueError(repo)


@app.command(name='update')
def github_cli():
    """Update GitHub information."""
    ldflex = ldflex_from_cache()
    rows = ldflex.query(
        '''
        SELECT ?repo_name WHERE {
            ?repo
                a gh:Repo ;
                rdfs:label ?repo_name .
        }
        '''
    )

    gh = Github()

    docs_dir = Path.cwd() / 'docs'

    if not docs_dir.is_dir():
        raise ValueError(
            f'{docs_dir} is considered to be docs directory but it does not '
            f'exist.',
        )

    target_dir = docs_dir / 'generated/octadocs-github'
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / 'context.json').write_text(json.dumps(
        {
            'updated_at': {
                '@type': 'xsd:dateTime',
            },
            '@vocab': 'https://octadocs.io/github/',
            'license': {
                '@type': 'gh:License',
            }
            # '@import': 'github',
        },
        indent=2,
    ))

    for row in rows:
        try:
            repo = gh.get_repo(row['repo_name'])
        except UnknownObjectException:
            logger.error(
                '%s is not a valid GitHub repository name.',
                row['repo_name'],
            )
            continue

        formatted_data = repo.raw_data
        formatted_data['@id'] = repo.html_url

        file_name = repo.full_name.replace('/', '__')
        (target_dir / f'{file_name}.json').write_text(json.dumps(
            formatted_data,
            indent=2,
        ))
