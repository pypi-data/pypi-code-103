import click

from octohot.cli.regex.colored_texts import Colors
from octohot.cli.github.utils import login, is_archived, check_rate_limit
from octohot.cli.github.pr import _pr
from multiprocessing.pool import ThreadPool


def job(client, c, repo, _click, _opts):
    # Make sure your current rate limit won't exceed
    check_rate_limit(client)

    try:
        if is_archived(repo):
            _click.echo(
                repo.pprint(c.warning('Skipping Repository because it is archived.', bold=True))
            )
            return None

        if repo.tainted():
            _click.echo(
                repo.pprint(c.success("Apply (Pull, change branch, add files, commit, push and make a optional PR)"))
            )
            repo.pull()
            repo.branch(_opts["branch_name"])
            repo.add()
            repo.commit(_opts["commit_name"], _opts["commit_description"])
            repo.push(_opts["branch_name"])
            if _opts["pull_request"] and repo.is_github():
                _pr(client, repo,
                    _opts["commit_name"],
                    _opts["commit_description"],
                    _opts["branch_name"],
                    _opts["default_branch"],
                    _opts["origin_branch"]
                    )
                repo.branch(repo.default_branch())
        else:
            _click.echo(
                repo.pprint(c.warning("nothing to commit, working tree clean"))
            )

        return None

    except Exception as e:
        _click.echo(
            repo.pprint(c.fail(e, bold=True))
        )

    return repo.name


@click.command()
@click.argument('branch_name')
@click.argument('commit_name')
@click.argument('commit_description')
@click.option('--pull_request', '-pr', is_flag=True, default=False)
@click.option('--default-branch', is_flag=True, required=False, default=False)
@click.option('--origin-branch', '-o', multiple=True, required=False)
def apply(branch_name, commit_name, commit_description, pull_request, default_branch, origin_branch):
    """Pull, create branch, add, commit, push and make an optional PR"""
    from octohot.cli.config import repositories
    gh_client = login()
    repo_owner = ''
    color = Colors()
    opts = {
        "branch_name": branch_name,
        "commit_name": commit_name,
        "commit_description": commit_description,
        "pull_request": pull_request,
        "default_branch": default_branch,
        "origin_branch": origin_branch
    }

    # Starting multiple threads
    threads = []
    pool = ThreadPool(processes=4)

    i = 1
    for repo in repositories:
        if not repo_owner:
            repo_owner = repo.owner
        print(color.bold('Starting Job: {} of {}'.format(i, len(repositories))))
        async_result = pool.apply_async(job, (gh_client, color, repo, click, opts))
        threads.append(async_result)
        i += 1

    # Return values based on each thread
    i = 1
    errors = []
    for thread in threads:
        error = thread.get()
        print(f"Completed: {i} of {len(repositories)}")
        if error:
            errors.append(error)
        i += 1

    pool.close()

    if errors:
        print('\nRepositories with Request Errors')
        for err in errors:
            print('- git@github.com:{}/{}'.format(repo_owner, err))
