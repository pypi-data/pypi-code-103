import click

from octohot.cli.regex.colored_texts import Colors


@click.command()
@click.argument('pr_title')
@click.argument('pr_comment')
@click.argument('branch_name')
@click.argument('default_branch')
@click.argument('origin_branch')
def pr(pr_title, pr_comment, branch_name, default_branch, origin_branch):
    from octohot.cli.config import repositories
    for repo in repositories:
        if repo.is_github() and repo.is_current_branch(branch_name):
            _pr(repo, pr_title, pr_comment, branch_name, default_branch, origin_branch)


def _pr(github_login, repo, pr_title, pr_comment, branch_name, default_branch, origin_branch):
    from github3 import exceptions
    color = Colors()
    github_repo = github_login.repository(repo.owner, repo.name)

    origin = 'master'
    if default_branch:
        origin = github_repo.default_branch
    if not default_branch and origin_branch:
        for b in origin_branch:
            try:
                origin = github_repo.branch(b).name
                break
            except exceptions.NotFoundError:
                continue

    pr = github_repo.create_pull(pr_title, origin, branch_name, pr_comment)
    click.echo(color.success("PR github repo %s PR %s branch %s: %s" % (repo.name, pr_title, branch_name, pr.url)))
