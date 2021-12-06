import argparse
import json
from json.decoder import JSONDecodeError
import textwrap
from typing import Any, Dict
from relycomply_client.client import RelyComplyClient
from gql.transport.exceptions import TransportQueryError
from dataclasses import dataclass
import toml
import sys

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import TOMLLexer, JsonLexer, YamlLexer

# from pygments_graphql import GraphqlLexer
from tabulate import tabulate
from termcolor import cprint

from . import RelyComplyGQLClient
from . import cleartoml
import yaml


@dataclass
class CliArguments:
    type: str
    action: str
    explain: bool
    output_format: str
    variables: Dict[str, Any]


class CliException(Exception):
    pass


class RelyComplyCLI:
    def __init__(self):
        self.gql = RelyComplyGQLClient()

    def run_command(self, args):
        try:
            cli_args = self.parse_args(args)
            result = self.execute_from_args(args)
            formatted_output = self.format_output(cli_args, result)
            print(formatted_output)
        except CliException as e:
            self.print_error(str(e))
        except TransportQueryError as e:
            self.print_error(e.errors[0]["message"])

    def execute_from_args(self, args):
        cli_args = self.parse_args(args)
        return self.execute(cli_args.type, cli_args.action, cli_args.variables)

    def get_argument_parser(self):
        parser = argparse.ArgumentParser(
            prog="rely",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="A command line interface for the RelyComply platform",
            epilog=textwrap.dedent(
                """
                Additional keyword arguments can be passed through to the RelyComply platform 
                in the form '--key=value'. These values can be json encoded objects.

                If the final argument is a file path it will attempt to load the file as a 
                TOML file. The additional keyword arguments are merged with the values of 
                the input TOML file. The command line arguments will take precedence.

                For more information please see https://docs.relycomply.com.
                """
            ),
        )
        parser.add_argument("type", help="the type of object to perform an action on")
        parser.add_argument("action", help="the action to perform")

        # Explain the graphql instructions
        parser.add_argument(
            "--explain",
            action="store_true",
            help="print out an explanation of the GraphQL commands executed",
        )

        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--toml",
            action="store_const",
            const="toml",
            dest="output_format",
            help="Output the results as toml or a formatted table (default)",
        )
        group.add_argument(
            "--json",
            action="store_const",
            const="json",
            dest="output_format",
            help="Output the results as json",
        )
        group.add_argument(
            "--yaml",
            action="store_const",
            const="yaml",
            dest="output_format",
            help="Output the results as yaml",
        )
        return parser

    def parse_args(self, args):
        parser = self.get_argument_parser()
        set_args, other_args = parser.parse_known_args(args)
        output_format = set_args.output_format or "toml"

        kwargs = [part for part in other_args if part.startswith("--")]

        try:
            kwargs = dict(part[2:].split("=", 1) for part in kwargs)
        except ValueError:
            raise CliException(
                "Keyword arguments must be of the form '--<key>=<value>'."
            )

        # We check if the value is json encoded, and decode it, otherwise it is just a string
        for key, value in kwargs.items():
            try:
                value = json.loads(value)
                kwargs[key] = value
            except JSONDecodeError as e:
                pass

        straight_args = [part for part in other_args if not part.startswith("--")]

        if not straight_args:
            filename = None
        elif len(straight_args) == 1:
            filename = straight_args[0]
        else:
            raise CliException("Too many input filename arguments")

        if filename:
            with open(filename) as f:
                file_kwargs = toml.load(f)
                variables = {**file_kwargs, **kwargs}
        else:
            variables = kwargs

        return CliArguments(
            type=set_args.type,
            action=set_args.action,
            explain=set_args.explain,
            output_format=output_format,
            variables=variables,
        )

    def execute(self, type, action, variables):
        field_type, field = self.get_graphql_field(type, action)
        if field_type == "mutation":
            return self.gql.execute_mutation(field, variables)
        elif field_type == "query":
            if action == "list":
                result = self.gql.execute_query(field, variables, _iter=True)
                return result
            elif action == "retrieve":
                result = self.gql.execute_query(field, variables, _only=True)
                if not result:
                    raise CliException("No matching items")

                return result

    def get_graphql_field(self, type, action):
        alias_mappings = self.gql.templates["aliases"]
        aliases = [
            *(
                (alias_action + alias_type, mutation_name, "mutation")
                for alias_type, alias_actions in alias_mappings.items()
                for alias_action, mutation_name in alias_actions.items()
            ),
            *((field, field, "mutation") for field in self.gql.mutation_fields),
            *((field, field, "query") for field in self.gql.query_fields),
        ]
        if action in ("list", "retrieve"):
            approximate_name = type + "s"
        else:
            approximate_name = action + type

        for alias, field, field_type in aliases:
            if alias.lower() == approximate_name.lower():
                return field_type, field

        # Find all the possible mutations
        possible_actions = [
            field[: -len(type.lower())]
            for field, _, _ in aliases
            if field.lower().endswith(type.lower())
        ]

        possible_query = [
            field
            for field, _, field_type in aliases
            if (type + "s").lower() == field.lower() and field_type == "query"
        ]

        # See if maybe it can be queried
        if possible_query:
            possible_actions.extend(["retrieve", "list"])

        if possible_actions:
            message = f"Action '{action}' not recognised for type '{type}', possible actions are:\n"
            raise CliException(
                message + "\n".join([f"  - {action}" for action in possible_actions])
            )
        else:
            raise CliException(f"Type '{type}' is not recognised")

    def format_output(self, cli_args, value):
        if cli_args.action == "list":
            return self.format_table_for_terminal(cli_args.output_format, value)
        else:
            return self.format_for_terminal(cli_args.output_format, value)

    def cell_output_for_table(self, value):
        if isinstance(value, dict):
            return json.dumps(value, indent=2)
        elif isinstance(value, list):
            return "\n".join(
                ["- " + self.cell_output_for_table(child) for child in value]
            )
        elif value is None:
            return ""
        else:
            return "\n".join(textwrap.wrap(str(value), 40))

    def format_table_for_terminal(self, output_format, nodes):

        if output_format == "json":
            return self.format_for_terminal(output_format, list(nodes))
        else:
            # TODO make this page correctly
            nodes = list(nodes)
            if nodes:
                columns = nodes[0].keys()
                headers = [key.replace(".", "\n") for key in columns]
                rows = [
                    [self.cell_output_for_table(node.get(key)) for key in columns]
                    for node in nodes
                ]
                return tabulate(rows, headers=headers, tablefmt="fancy_grid")

            else:
                raise CliException(f"No matching items")

    def format_for_terminal(self, output_format, value):

        if output_format == "json":
            code = json.dumps(value, indent=2)
            lexer = JsonLexer()
        elif output_format == "yaml":
            lexer = YamlLexer()
            code = yaml.dump(value)
        elif output_format == "toml":
            lexer = TOMLLexer()
            code = cleartoml.dumps(value)
        else:
            raise CliException(f"Unknown format '{output_format}'.")

        if sys.stdout.isatty():
            return highlight(code, lexer, TerminalFormatter())
        else:
            return code

    def print_error(self, message):
        cprint(message, "red", file=sys.stderr)
