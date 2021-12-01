import time
import click
from octohot.cli.github.utils import is_archived
from octohot.cli.regex.colored_texts import Colors
from threading import Thread

color = Colors()


def workflow(repo):
    try:
        if is_archived(repo):
            click.echo(repo.pprint(color.warning('Skipping Repository because it is archived.', bold=True)))
            return
        click.echo(repo.pprint(color.success('Sync: Clone, reset, delete unpushed Branches, pull')))
        repo.clone()
        repo.reset()
        repo.branch(repo.default_branch())
        repo.delete_unpushed_branches()
        repo.pull()
    except Exception as e:
        click.echo(
            repo.pprint(color.fail(e, bold=True))
        )


@click.command()
def sync():
    """Sync: Clone, reset, delete unpushed Branches, pull"""
    from octohot.cli.config import repositories

    threads = []
    i = 0
    count = 0
    for repo in repositories:
        print(color.bold('Repositories: {} of {}'.format(i + 1, len(repositories))))
        worker = Thread(target=workflow, args=(repo,))
        threads.append(worker)
        worker.start()

        count += 1
        if count >= 10:
            count = 0
            time.sleep(10)

        i += 1

    for index, thread in enumerate(threads):
        thread.join()
        print(color.bold('Completed: {} of {}'.format(index + 1, len(threads))))
