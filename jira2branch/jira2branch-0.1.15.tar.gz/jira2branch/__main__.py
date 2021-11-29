import os
import re
import string
from configparser import ConfigParser
from pathlib import Path
from typing import Optional

import click
from git import Repo, InvalidGitRepositoryError, NoSuchPathError, GitCommandError
import gitlab
from gitlab.v4.objects.merge_requests import ProjectMergeRequest
from halo import Halo
from jira import JIRA, JIRAError
from unidecode import unidecode


class JIRACredentials:
    file = ''
    url = ''
    username = ''
    password = ''
    email = ''
    token = ''


def get_credentials() -> Optional[JIRACredentials]:
    secrets = JIRACredentials()
    secrets_file_path = Path.home().joinpath('.j2b')
    secrets_file_name = 'secrets.ini'
    secrets_file = secrets_file_path.joinpath(secrets_file_name)

    secrets.file = str(secrets_file)

    if secrets_file.exists():
        parser = ConfigParser()
        parser.read(secrets_file)
        jira_credentials_section = parser["JIRA CREDENTIALS"]
        secrets.url = jira_credentials_section.get("url")
        secrets.email = jira_credentials_section.get("email")
        secrets.token = jira_credentials_section.get("token")
        secrets.username = jira_credentials_section.get("username")
        secrets.password = jira_credentials_section.get("password")
    else:
        os.makedirs(secrets_file_path, exist_ok=True)
        secrets_file.touch()
        with secrets_file.open('w') as f:
            f.writelines(["[JIRA CREDENTIALS]\n\n",
                          "# url = \n",
                          "# email = \n",
                          "# username = \n",
                          "# password = \n",
                          "# token = \n"])
        click.echo(f'Created empty secrets file under {secrets_file}, please configure it first')
        return None

    return secrets


def get_jira_rest_endpoint() -> JIRA:
    credentials = get_credentials()

    if not credentials and (not credentials.email or not credentials.token):
        click.secho(f"Invalid configuration, please check {credentials.file}", fg='red')
        exit()

    spinner = Halo(text='Connecting to JIRA API', spinner='dots')
    spinner.start()

    jira = None

    if credentials.email and credentials.token:
        try:
            jira = JIRA(credentials.url, basic_auth=(credentials.email, credentials.token),
                        validate=True)
        except JIRAError as error:
            print(error)
            exit(1)
        finally:
            spinner.stop()
        return jira
    elif credentials.username and credentials.password:
        try:
            jira = JIRA(credentials.url, auth=(credentials.username, credentials.password),
                        validate=True)
        except JIRAError as error:
            print(error)
            exit(1)
        finally:
            spinner.stop()
        return jira
    else:
        spinner.stop()
        raise IOError(
            f"Invalid or missing credentials file! Check {credentials.file}, I might have created it for you")


def get_branch_name_from_issue(issue_id: str) -> [str]:
    jira = None
    issue = None

    try:
        jira = get_jira_rest_endpoint()
    except IOError:
        click.secho('Failed to connect to JIRA, please check configuration', fg='red')
        exit()

    try:
        spinner = Halo(text=f'Fetching JIRA issue {issue_id}', spinner='dots')
        spinner.start()
        issue = jira.issue(issue_id)
        spinner.stop()
    except JIRAError as error:
        print(error)
        exit(1)

    issue_type = issue.fields.issuetype.name

    if 'task' in str.lower(issue_type):
        issue_type = 'feat'
    else:
        issue_type = 'fix'

    title = f'{issue.fields.summary}'

    return [Utils.issue_title_to_branch_name(issue_id, title, issue_type), f'{issue_id}: {title}']


def create_branch(branch_name, push=False, target: Path = Path.cwd(), source_branch='develop'):
    try:
        repo = Repo(target)

        stashed_changes = False

        #  if dirty stash all changes and apply them on the new branch
        if repo.is_dirty():
            repo.git.execute(['git', 'stash'])
            stashed_changes = True

        # check if develop exists otherwise switch to master otherwise switch to main
        for branch in [source_branch, 'master', 'main']:
            spinner = Halo(text=f'Checking if source branch {branch} exists...', spinner='dots')
            spinner.start()
            if check_if_branch_exists(repo, branch):
                source_branch = branch
                click.secho(f'YES', fg='green')
                spinner.stop()
                break
            else:
                click.secho(f'NO', fg='red')

        #  check if a branch by this name already exists locally
        click.secho('Checking if branch already exists on local repository...')
        if check_if_branch_is_local(repo, branch_name):
            click.secho('Local branch already exists, switching to it', fg='blue')
            switch_to_branch(repo, branch_name)
            return source_branch

        #  check if a branch by this name already exists on remote
        spinner = Halo(text='Checking if branch already exists on remote repository...', spinner='dots')
        spinner.start()
        if not check_if_branch_exists(repo, branch_name):
            click.secho('Branch name IS available', fg='green')
        else:
            click.secho('A remote branch by that name already exists... aborting', fg='green')
            raise Exception('A remote branch by that name already exists... aborting')
        spinner.stop()

        #  we're good to go
        #  create MR branch from latest develop or master
        try:
            spinner = Halo(text='Fetching all remote branches', spinner='dots')
            spinner.start()
            repo.git.execute(['git', 'fetch', '--all'])
            spinner.stop()
            click.secho('Fetched all remote branches', fg='green')
        except Exception as err:
            print(err)
            spinner.stop()
        try:
            spinner = Halo(text=f'Creating local branch {branch_name} from {source_branch}', spinner='dots')
            spinner.start()
            repo.git.execute(['git', 'checkout', source_branch])
            repo.git.execute(['git', 'pull'])
            repo.git.execute(['git', 'branch', branch_name])
            spinner.stop()
            click.secho(f'Created local branch {branch_name}', fg='green')
            switch_to_branch(repo, branch_name)
        except Exception as err:
            click.secho('Failed to create local branch...')
            print(err)
            spinner.stop()

        # setting remote tracking branch
        upstream_branch_command = ['git', 'push', '-u', 'origin', f'{branch_name}']
        if push:
            repo.git.execute(upstream_branch_command)
        else:
            click.secho('NOTE: Branch NOT pushed to remote (use with -p to push automatically)', fg='blue')
            click.secho('Whenever you decide to push your changes to remote use the following command:', fg='blue')
            upstream_branch_command = ' '.join(upstream_branch_command)
            click.secho(''.ljust(len(upstream_branch_command), '#'))
            click.echo(f' > {upstream_branch_command}')
            click.secho(''.ljust(len(branch_name), '#'))

        if stashed_changes:
            repo.git.execute(['git', 'stash', 'pop'])

        click.secho('Switching to new branch. Good luck!', fg='green')

    except InvalidGitRepositoryError as err:
        click.secho(err, fg='red')
        raise err
    except NoSuchPathError as err:
        click.secho(err, fg='red')
        raise err
    return source_branch


def check_if_branch_is_local(repo, branch_name) -> bool:
    result = repo.git.execute(['git', 'branch', '--list', branch_name])
    if not result:
        return False
    return True


def check_if_branch_exists(repo, branch_name) -> bool:
    remote_branch = repo.git.execute(['git', 'ls-remote', '--heads', 'origin', branch_name])
    if remote_branch:
        return True
    return False


def switch_to_branch(repo, branch_name):
    repo.git.execute(['git', 'checkout', branch_name])


## MERGE REQUEST CREATION

# This requires:
# TOKEN: have it setup in secrets file
# PROJECT_ID: infer from repo?
# SOURCE_BRANCH
# TARGET_BRANCH: develop by default
# TITLE: infer from JIRA issue title
# DESCRIPTION: default is link to JIRA issue, user can then edit once MR has been created

def create_merge_request(target: Path, source_branch: str, target_branch: str, issue_id: str, issue_url: str,
                         title: str):
    spinner = Halo(text=f'Creating MR for {issue_id}', spinner='dots')
    spinner.start()

    repo = Repo(target)

    project_name = None
    project_name_with_namespace = None
    project = None

    try:
        project_name_with_namespace = repo.git.execute(['git', 'remote', 'get-url', 'origin'])
        project_name_with_namespace = re.findall(r'git@gitlab\.com:(.+)\.git', project_name_with_namespace)[0]
        assert project_name_with_namespace
        project_name = project_name_with_namespace.split("/")[-1]
        assert project_name
    except GitCommandError as err:
        click.secho("Failed to parse repository name, aborting", fg='red')
        click.echo(err)

    # gl = gitlab.Gitlab.from_config('infraspeak', [str(Path.home().joinpath('.j2b').joinpath('gitlab_secrets.ini'))])
    gl = gitlab.Gitlab('https://gitlab.com/', private_token='EA7v3zT8oW84HX2BYz96')
    gl.auth()
    # mrs = gl.mergerequests.list()
    project = gl.projects.get(project_name_with_namespace)

    # MR DESCRIPTION
    """
    Uses the MR template as defined in project (if set) instead of a custom one.
    Checks and replaces explicit references to Infraspeak's Jira issue URLs
    """
    description = f'[{issue_id}]({issue_url})'

    if hasattr(project, 'merge_requests_template'):
        mr_template = project.merge_requests_template

        if mr_template:
            description = mr_template.replace('https://infraspeak.atlassian.net/browse/', f'[{issue_id}]({issue_url})')

    merge_requests_for_issue: [ProjectMergeRequest] = project.mergerequests.list(search=issue_id)

    # filter opened and locked MRs
    merge_requests_for_issue = [mr for mr in merge_requests_for_issue if mr.state not in ['merged', 'locked']]

    # this check is probably pointless...
    if merge_requests_for_issue:
        spinner.stop()
        click.secho(f'One or more pending MR already exist for this issue... aborting', fg='red')
        exit(1)

    # check if upstream branch is set
    set_upstream_branch = True
    try:
        upstream_branch = repo.git.execute(["git", "rev-parse", "--abbrev-ref", f"{source_branch}@{{upstream}}"])
        if source_branch in upstream_branch:
            set_upstream_branch = False
    except GitCommandError:
        click.secho(f"No upstream configured for {source_branch}", fg='blue')

    if set_upstream_branch:
        try:
            repo.git.execute(["git", "push", "-u", "origin", source_branch])
        except GitCommandError as err:
            click.secho(f'Something failed while trying to push...', fg='red')
            click.echo(err)
            exit(1)
    else:
        # only create the MR if there are pending commits
        pending_commits = repo.git.execute(["git", "log", "@{upstream}.."])

        # or merges
        pending_merges = repo.git.execute(["git", "log", f"{target_branch}.."])

        if not pending_commits and not pending_merges:
            click.secho(f'No commits to push, nothing to do here!', fg='green')
            exit(1)
        else:
            try:
                repo.git.execute(["git", "push"])
            except GitCommandError as err:
                click.secho(f'Something failed while trying to push...', fg='red')
                click.echo(err)
                exit(1)

    # WE ARE GOOD TO GO!
    title = f'{title}'  # MARK THE MR AS WORK IN PROGRESS

    mr_payload = {'source_branch': source_branch,
                  'target_branch': target_branch,
                  'title': title,
                  'squash': True,
                  'remove_source_branch': True,
                  'description': description
                  }

    try:
        mr = project.mergerequests.create(mr_payload)
        spinner.stop()
        click.secho(f'Created MR {mr.title}', fg='green')
    except Exception as err:
        spinner.stop()
        click.secho(f'Failed to create MR', fg='red')
        click.echo(err)

    return None


class Utils:

    @staticmethod
    def issue_title_to_branch_name(issue_id: str, title: str, issue_type: str) -> str:

        separator = '-'

        title = unidecode(title)  # replace non ascii characters
        title = title.replace(' ', separator)  # no spaces

        title = re.sub(r'[^\w\d-]', separator, title)  # replace all non word, non digit characters
        title = re.sub(r'-+', separator, title)  # remove repetitions
        title = re.sub(r'^-', '', title)  # trim start
        title = re.sub(r'-$', '', title)  # trim end
        title = title.strip()  # trim both ends

        title = str.lower(title)

        allowed_chars = string.ascii_letters + string.digits + '-'

        branch_title = ''
        for c in title:
            if c in allowed_chars:
                branch_title += c

        branch_title = f'{issue_type}/{issue_id}_{branch_title}'

        # keep the branch name under 255 chars
        branch_title = branch_title[:255]

        return branch_title


@click.command()
@click.argument('issue_id_or_url')
@click.option('-n', '--name-only', is_flag=True, default=False,
              help='Generates the branch name and prints it, no actual branch will be created (default is False)')
@click.option('-p', '--push', is_flag=True, default=False,
              help='Push newly created branch to remote (default is False)')
@click.option('-t', '--target', type=Path, default=Path.cwd(),
              help='Target repository (default is current directory)')
@click.option('-r', '--merge-request', is_flag=True, default=False,
              help='Create merge request. Requires --push. (default is False)')
@click.option('-s', '--source-branch', default='develop',
              help='Source branch')
def cli(issue_id_or_url, name_only, push, target: Path, merge_request: bool, source_branch: str):
    """Simple program that takes a JIRA issue ID and creates a new local and tracking remote branch"""

    issue_id = issue_id_or_url

    if '/' in issue_id_or_url:
        issue_id = issue_id_or_url.split('/')[-1]

    # print(os.getcwd())
    # repo = Repo(os.getcwd())
    # assert not repo.bare

    names = get_branch_name_from_issue(issue_id)
    branch_name = names[0]
    mr_title = names[1]
    # print(branch_name, end='\n')
    # sys.stdout.write(branch_name)

    if name_only:
        click.secho('BRANCH NAME: '.ljust(len(branch_name), '#'), fg='green')
        click.echo(branch_name)
        click.secho(''.rjust(len(branch_name), '#'), fg='green')

        click.echo('')

        click.secho('MR TITLE: '.ljust(len(mr_title), '#'), fg='green')
        click.echo(mr_title)
        click.secho(''.rjust(len(mr_title), '#'), fg='green')

        if check_if_branch_exists(Repo(target), branch_name):
            click.secho(f'WARNING: a remote branch by that name already exists', fg='red')
    else:
        target_branch = None
        try:
            target_branch = create_branch(branch_name, push, target, source_branch)
        except Exception:
            exit(1)
        if target_branch and merge_request:
            credentials = get_credentials()
            create_merge_request(target, branch_name, target_branch, issue_id,
                                 f'{credentials.url}/browse/{issue_id}', mr_title)


if __name__ == '__main__':
    cli()
