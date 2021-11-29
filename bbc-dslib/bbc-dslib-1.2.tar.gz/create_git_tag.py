from git import Repo
from git.exc import GitCommandError

from version import __version__


repo = Repo()
try:
    print(f'Create git tag "{__version__}"')
    new_tag = repo.create_tag(__version__, message=f'Automatic tag "{__version__}"')
except GitCommandError as exception:
    raise ValueError(f'Invalid version "{__version__}": change it in dslib/__init__.py') from exception
print('Pushing local changes to remote git repository')
repo.remotes.origin.push(new_tag)
