# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import click
from lxml import etree


def _print_commands(command, command_str):
    if isinstance(command, click.Group):
        for name, value in command.commands.items():
            _print_commands(value, f"{command_str} {name}")
    else:
        click.echo(command_str)


def print_commands(ctx, param, value, **kwargs):
    """Print a list of all commands a group contains and exit."""
    if not value or ctx.resilient_parsing:
        return

    command = ctx.command
    command_str = command.name

    parent = command.parent
    while parent is not None:
        command_str = f"{parent.name} {command_str}"
        parent = parent.parent

    _print_commands(command, command_str)
    ctx.exit()


def print_xmlhelp(ctx, param, value, **kwargs):
    """Print the xmlhelp message of a command and exit."""
    if not value or ctx.resilient_parsing:
        return

    program_elem = ctx.command.to_xml()

    # Always list all arguments first.
    sorted_params = sorted(
        ctx.command.params,
        key=lambda param: param.param_type_name,
    )

    for index, _param in enumerate(sorted_params):
        if (
            _param.name
            not in [
                "help",
                "xmlhelp",
                "version",
                "env_exec",
            ]
            and not _param.exclude_from_xml
        ):
            program_elem.append(_param.to_xml(index))

    xml = etree.tostring(
        program_elem,
        pretty_print=True,
        xml_declaration=True,
        encoding="UTF-8",
    )

    # Do not print the additional newline.
    click.echo(xml.decode()[:-1])
    ctx.exit()


def print_version(ctx, param, value, **kwargs):
    """Print the version of a command or group and exit."""
    if not value or ctx.resilient_parsing:
        return

    if ctx.command.version is not None:
        click.echo(ctx.command.version)

    ctx.exit()
