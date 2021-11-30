"""
Translate an options data structure into command line args
"""
import argparse
import inspect
import sys
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

import dict_tools.update


def __init__(hub):
    hub.config.args.DEFAULT = object()


def _keys(opts):
    """
    Return the keys in the right order
    """
    return sorted(opts, key=lambda k: (opts[k].get("display_priority", sys.maxsize), k))


def gather(
        hub, raw: Dict[str, Any], cli: str, parse_cli: bool
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Return the cli arguments as they are parsed
    """
    if not parse_cli:
        return {}, {}
    hub.config.args.parser.init()
    raw_cli = hub.config.args.init.get_cli(raw, cli)
    hub.config.args.init.subparsers(raw, cli)
    hub.config.args.init.setup(raw_cli)
    cli_args = hub.config.args.init.parse()
    cli_args = hub.config.args.init.render(cli_args, raw_cli)
    cli_args = hub.config.args.init.clean_defaults(cli_args)
    return cli_args, raw_cli


def clean_defaults(hub, cli_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    If anyone did not pass in an argument then the key will match the
    bad default and needs to be removed
    """
    ret = {}
    for key, val in cli_args.items():
        if val is not hub.config.args.DEFAULT:
            ret[key] = val

    return ret


def get_cli(hub, raw: Dict[str, Any], cli: str) -> Dict[str, Any]:
    """
    Gather the arguments that need to be parsed by the CLI
    """
    ret = {}
    main = raw.get(cli, {}).get("CLI_CONFIG")
    main_raw = raw.get(cli, {}).get("CONFIG")

    for key, data in main.items():
        ret[key] = {}
        dict_tools.update.update(ret[key], data)
        if key in main_raw:
            dict_tools.update.update(ret[key], main_raw[key])
        if "source" in data:
            src = raw.get(data["source"], {}).get("CONFIG", {}).get(key)
            if src is not None:
                dict_tools.update.update(ret[key], src)
        if "default" in ret[key]:
            ret[key]["default"] = hub.config.args.DEFAULT
    ret.update(hub.config.version.CONFIG)
    return ret


def subparsers(hub, raw: Dict[str, Any], cli: str):
    """
    Look over the data and extract and set up the subparsers for subcommands
    """
    subs = raw.get(cli, {}).get("SUBCOMMANDS")
    if not subs:
        return

    for arg in _keys(subs):
        if arg in ("_argparser_",):
            continue
        comps = subs[arg]
        kwargs = {}
        if "help" in comps:
            kwargs["help"] = comps["help"]
        if "desc" in comps:
            kwargs["description"] = comps["desc"]
        hub.config.args.parser.add(arg, **kwargs)

def setup(hub, raw_cli: Dict[str, Any]) -> Dict[str, Any]:
    """
    Take in a pre-defined dict and translate it to args

    opts dict:
        <arg>:
            [group]: foo
            [default]: bar
            [action]: store_true
            [options]: # arg will be turned into --arg
              - '-A'
              - '--cheese'
            [choices]:
              - foo
              - bar
              - baz
            [nargs]: +
            [type]: int
            [dest]: cheese
            help: Some great help message
    """
    # TODO: This should be broken up
    defaults = {}
    sub_groups = {}
    groups = {}
    ex_groups = {}
    for arg in _keys(raw_cli):
        if arg in ("_argparser_",):
            continue
        comps = raw_cli[arg]
        positional = comps.pop("positional", False)
        if positional:
            args = [arg]
        else:

            args = [f"--{arg.replace('_', '-')}"]
            for o_str in comps.get("options", ()):
                if len(o_str) == 1:
                    o_str = f"-{o_str}"
                elif not o_str.startswith("-"):
                    o_str = f"--{o_str}"
                if o_str not in args:
                    args.append(o_str)
        kwargs = {}
        kwargs["action"] = action = comps.get("action", None)

        if action is None:
            # Non existing option defaults to a StoreAction in argparse
            action = hub.config.args.PARSER._registry_get("action", action)

        if isinstance(action, str):
            signature = inspect.signature(
                hub.config.args.PARSER._registry_get("action", action).__init__
            )
        else:
            signature = inspect.signature(action.__init__)

        for param in signature.parameters:
            if param == "self" or param not in comps:
                continue
            if param == "dest":
                kwargs["dest"] = comps.get("dest", arg)
                continue
            if param == "help":
                kwargs["help"] = comps.get("help", "THIS NEEDS SOME DOCUMENTATION!!")
                continue
            if param == "default":
                defaults[comps.get("dest", arg)] = comps[param]
            kwargs[param] = comps[param]

        if "ex_group" in comps:
            group = comps["ex_group"]
            if group not in ex_groups:
                ex_groups[group] = hub.config.ARGS[
                    "parser"
                ].add_mutually_exclusive_group()
            ex_groups[group].add_argument(*args, **kwargs)
            continue
        if "subcommands" in comps:
            subs = comps["subcommands"]
            if not isinstance(subs, list):
                subs = [subs]
            for sub in subs:
                if sub == "_global_":
                    if "subs" not in hub.config.ARGS:
                        continue
                    hub.config.PARSER.add_argument(*args, **kwargs)
                    for named, sparse in hub.config.ARGS["subs"].items():
                        if "group" in comps:
                            group = comps["group"]
                            if named not in sub_groups:
                                sub_groups[named] = {}
                            if group not in sub_groups[named]:
                                sub_groups[named][group] = sparse.add_argument_group(
                                    group
                                )
                            sub_groups[named][group].add_argument(*args, **kwargs)
                        else:
                            sparse.add_argument(*args, **kwargs)
                sparse = hub.config.ARGS.get("subs", {}).get(sub)
                if not sparse:
                    # Maybe raise exception here? Malformed config?
                    continue
                sparse.add_argument(*args, **kwargs)
            continue
        if "group" in comps:
            group = comps["group"]
            if group not in groups:
                groups[group] = hub.config.PARSER.add_argument_group(group)
            groups[group].add_argument(*args, **kwargs)
            continue
        hub.config.args.PARSER.add_argument(*args, **kwargs)

    return defaults


def parse(
        hub,
        args: List[str] = None,
        namespace: argparse.Namespace = None,
        only_parse_known_arguments: bool = False,
) -> Dict[str, Any]:
    """
    Parse the command line options
    """
    if only_parse_known_arguments:
        opts, unknown_args = hub.config.PARSER.parse_known_args(args, namespace)
        opts_dict = opts.__dict__
        opts_dict["_unknown_args_"] = unknown_args
    else:
        opts = hub.config.args.PARSER.parse_args(args, namespace)
        opts_dict = opts.__dict__
    hub.SUBPARSER = opts_dict.get("_subparser_", None)
    return opts_dict


def render(hub, cli_args: Dict[str, Any], raw_cli: Dict[str, Any]) -> Dict[str, Any]:
    """
    For options specified as such, take the string passed into the cli and
    render it using the specified render flag
    """
    for key, val in raw_cli.items():
        if key not in cli_args:
            continue
        if "render" not in val:
            continue
        if val["default"] != cli_args[key]:
            # The value was changed, render it
            cli_args[key] = hub.config.render.init.process(val["render"], cli_args[key])
    return cli_args
