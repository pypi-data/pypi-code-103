import pytest
from ..engine import Engine
from ..subcommand import BaseSubcommand


class ExampleSubcommand(BaseSubcommand):
    def name(self):
        return "example-subcommand"

    def register_args(self, subparser):
        subparser.add_argument("-f", "--foobar", default=False, action="store_true")

    def run(self, args):
        name = "world"
        if args.get("foobar"):
            name = "foobar"
        return "Hello, " + name


def test_engine_init():
    e = Engine("test", [ExampleSubcommand()])
    result = e.run(["example-subcommand", "--foobar"])
    assert result == "Hello, foobar"


def test_engine_no_args():
    e = Engine("test", [ExampleSubcommand()])
    result = e.run(["example-subcommand"])
    assert result == "Hello, world"


def test_engine_bad_argument():
    e = Engine("test", [ExampleSubcommand()])
    with pytest.raises(SystemExit):
        e.run(["example-subcommand", "--bad-arg"])


def test_engine_wrong_subcommand():
    e = Engine("test", [ExampleSubcommand()])
    with pytest.raises(SystemExit):
        e.run(["wrong-subcommand"])


def test_engine_no_subcommands():
    with pytest.raises(
        ValueError, match="Engine must contain at least one subcommand!"
    ):
        _ = Engine("test", [])
