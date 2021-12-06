import argparse
from typing import Dict, Union, List, Tuple, Optional

__all__ = ['set_base_parser', 'add_arg_group', 'KVAppendAction', 'get_parsed_args']


def set_base_parser() -> argparse.ArgumentParser:
    """
    Set base parser
    """
    parser = argparse.ArgumentParser()

    return parser


def add_arg_group(parser: argparse.ArgumentParser, title: str):
    """
    Add a sub group in parser
    :param parser: original parser
    :param title: sub group parser name
    :return: sub parser group
    """
    return parser.add_argument_group(title)


def kwargs2list(kwargs: Dict) -> List[str]:
    import json
    args = []
    for k, v in kwargs.items():
        k = k.replace('_', '-')
        if v is not None:
            if isinstance(v, bool):
                if v:
                    args.append(f'--{k}')
            elif isinstance(v, list):  # for nargs
                args.extend([f'--{k}', *(str(vv) for vv in v)])
            elif isinstance(v, dict):
                args.extend([f'--{k}', [json.dumps(v)]])
            else:
                args.extend([f'--{k}', str(v)])
    return args


def get_parsed_args(kwargs: Dict[str, Union[str, int, bool]], parser: argparse.ArgumentParser,
                    parser_name: str = None) -> Tuple[argparse.Namespace, List[str]]:
    args = kwargs2list(kwargs)
    try:
        p_args, unknown_args = parser.parse_known_args(args)
        if unknown_args:
            from ..logging import default_logger
            default_logger.warning(
                f'parser {parser_name} can not '
                f'recognize the following args: {unknown_args}, '
                f'they are ignored. if you are using them from a global args (e.g. Flow), '
                f'then please ignore this message')
    except SystemExit:
        raise ValueError('bad arguments "%s" with parser %r, '
                         'you may want to double check your args ' % (args, parser))
    return p_args, unknown_args


def parse_arg(v: str) -> Optional[Union[bool, int, str, list, float]]:
    """
    Parse the arguments from string to `Union[bool, int, str, list, float]`.

    :param v: The string of arguments
    :return: The parsed arguments list.
    """
    import re
    m = re.match(r'^[\'"](.*)[\'"]$', v)
    if m:
        return m.group(1)

    if v.startswith('[') and v.endswith(']'):
        # function args must be immutable tuples not list
        tmp = v.replace('[', '').replace(']', '').strip().split(',')
        if len(tmp) > 0:
            return [parse_arg(vv.strip()) for vv in tmp]
        else:
            return []
    try:
        v = int(v)  # parse int parameter
    except ValueError:
        try:
            v = float(v)  # parse float parameter
        except ValueError:
            if len(v) == 0:
                # ignore it when the parameter is empty
                v = None
            elif v.lower() == 'true':  # parse boolean parameter
                v = True
            elif v.lower() == 'false':
                v = False
    return v


class KVAppendAction(argparse.Action):
    """argparse action to split an argument into KEY=VALUE form
    on the first = and append to a dictionary.
    This is used for setting up --env
    """

    def __call__(self, parser, args, values, option_string=None):
        """
        call the KVAppendAction


        .. # noqa: DAR401
        :param parser: the parser
        :param args: args to initialize the values
        :param values: the values to add to the parser
        :param option_string: inherited, not used
        """
        import json

        d = getattr(args, self.dest) or {}
        for value in values:
            d.update(json.loads(value))

        setattr(args, self.dest, d)
