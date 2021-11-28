import click
import requests
from dateutil.parser import parse
from enum import Enum
import json
from types import SimpleNamespace


class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")

    def resolve_command(self, ctx, args):
        # always return the full command name
        _, cmd, args = super().resolve_command(ctx, args)
        return cmd.name, cmd, args


class NotRequiredIf(click.Option):
    def __init__(self, *args, **kwargs):
        self.not_required_if = kwargs.pop("not_required_if")
        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs["help"] = (
            kwargs.get("help", "")
            + " NOTE: This argument is mutually exclusive with %s"
            % self.not_required_if
        ).strip()
        super(NotRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        we_are_present = self.name in opts
        other_present = self.not_required_if in opts and opts[self.not_required_if]

        if other_present:
            if we_are_present:
                raise click.UsageError(
                    "Illegal usage: `%s` is mutually exclusive with `%s`"
                    % (self.name, self.not_required_if)
                )
            else:
                self.prompt = None

        return super(NotRequiredIf, self).handle_parse_result(ctx, opts, args)


def dict_to_namespace(dictionary):
    return json.loads(
        json.dumps(dictionary), object_hook=lambda item: SimpleNamespace(**item)
    )


def convert_time(time_str):
    if time_str:
        date = parse(time_str)
        # date = date.replace(tzinfo=None)
        return date


def date_format(date, second=False):
    format = "%y-%m-%d %H:%M"
    if second:
        format += ":%S"

    if date:
        return date.strftime(format)


def api_health_check(url):
    try:
        res = requests.get(url + "/api/healthz")
        if res.status_code != 404:
            raise ValueError()

    except (requests.exceptions.ConnectionError, ValueError):
        sprint(
            f"Server is not responding. Please check url({url}) is correct.",
            PrintType.FAILED,
        )
        sprint("\n\tSetup `url` with `ocean init --url <url>`.")
        return False

    return True


class PrintType(Enum):
    NORMAL = 0
    SUCCESS = 1
    FAILED = 2
    WORNING = 3


def sprint(msg="", type=PrintType.NORMAL, nl=True):
    if type == PrintType.NORMAL:
        click.echo(msg, nl=nl)
    elif type == PrintType.SUCCESS:
        click.secho("\u2713" + f" {msg}", fg="green", bold=True, nl=nl)
    elif type == PrintType.FAILED:
        click.secho("\u2717" + f" {msg}", fg="red", bold=True, nl=nl)
    elif type == PrintType.WORNING:
        click.secho("\u26A0" + f" {msg}", fg="yellow", bold=True, nl=nl)
