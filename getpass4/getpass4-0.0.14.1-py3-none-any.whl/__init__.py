def getpass(prompt: str, char=tuple('*'), mnbe: bool = False):
    """"""
    from getpass4.__getpass4__ import __getpass__
    return __getpass__(prompt=prompt, char=char, mnbe=mnbe)
from getpass4.gp4_help import help_
getpass.__doc__ = help_
del help_
