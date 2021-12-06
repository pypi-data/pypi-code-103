from time import gmtime, strftime
import click


def echo(*args, **kwargs):
    click.secho(*args, **kwargs)


def stdout_msg(msg, **kwargs):
    echo(f"[{get_time()}]", fg="cyan", nl=False)
    echo(f" - {msg}", **kwargs)


def get_time():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())

