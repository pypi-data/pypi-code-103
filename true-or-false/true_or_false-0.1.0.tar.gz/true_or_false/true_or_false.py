from logging import getLogger

logger = getLogger(__name__)


def true_or_false(s):
    ''' Determine (educated guess) whether an input value is True
    or False.  Input can be a bool, dict, int or str.  This is
    useful for determining the value of a parameter as passed
    in via environment variable, cli, config file or plain
    python code.

    Examples of True values:
        str: ['true', 't', '1', 'yes', 'y', 't', 'oui']
        bool: True
        dict: {'a': 1} # any non empty dictionary
        list: [0]  # any list not zero length
    Examples of False values:
        str FALSES = ['false', 'f', '0', 'no', 'n', 'non']
        bool: False
        dict: {}  # empty dictionary
        list: []  # empty list

    '''
    TRUES = ['true', 't', '1', 'yes', 'y', 't', 'oui']
    FALSES = ['false', 'f', '0', 'no', 'n', 'non']

    if s is None:
        return False
    if isinstance(s, bool):
        return s
    if isinstance(s, int):
        if s == 0:
            return False
        else:
            return True
    if isinstance(s, list):
        return len(s) != 0
    if isinstance(s, dict):
        return bool(s)
    if s.strip().lower() in TRUES:
        return True
    elif s.strip().lower() in FALSES:
        return False
    else:
        logger.warning(f"Cannot determine True/False from {s}")
        return None
