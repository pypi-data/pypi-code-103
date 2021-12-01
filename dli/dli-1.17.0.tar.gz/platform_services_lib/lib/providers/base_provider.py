#
# Copyright (C) 2019 IHS Markit.
# All Rights Reserved
#

from typing import Optional
from collections import namedtuple
try:
    from injector import Module
except ModuleNotFoundError:
    Module = object  # type: ignore

Dependency = namedtuple(
    'Dependency',
    ['binding_key', 'method', 'scope']
)


class BaseModule(Module):
    """
    Defines a injector module with some predefined lifecyle methods.
    Please make future dependencies inherit from this class as it
    greatly simplifies testing.

    ----

    Supporting flask extensions can be done like this.

    https://github.com/alecthomas/flask_injector#supporting-flask-extensions
    """
    config_class: Optional[type] = None

    def __init__(self, **kwargs):
        super().__init__()
        if self.config_class:
            self.config = self.config_class(**kwargs)
