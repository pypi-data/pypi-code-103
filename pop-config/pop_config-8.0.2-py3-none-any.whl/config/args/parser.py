import argparse

def __init__(hub):
    hub.config.args.DEFAULT = object()
    hub.config.args.PARSER = None
    hub.config.args.SUBPARSER = None
    hub.config.args.SUBPARSERS = {}


def init(hub) -> argparse.ArgumentParser:
    if hub.config.args.PARSER is None:
        hub.config.args.PARSER = argparse.ArgumentParser()

def init_sub(hub):
    hub.config.args.parser.init()
    if hub.config.args.SUBPARSER is None:
        hub.config.args.SUBPARSER = hub.config.args.PARSER.add_subparsers(dest="_subparser_")

def add(hub, arg: str, **kwargs):
    hub.config.args.parser.init_sub()
    hub.config.args.SUBPARSERS[arg] = hub.config.args.SUBPARSER.add_parser(arg, **kwargs)
