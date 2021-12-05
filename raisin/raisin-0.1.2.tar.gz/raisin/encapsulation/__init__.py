#!/usr/bin/env python3

"""
** Used to encapsulate packets before sending them. **
------------------------------------------------------

In particular, when the user wants to execute several tasks through a network,
they are split into small packets. These packets are made up of the function
and the arguments specific to each task.
"""

__all__ = ['Argument', 'Function', 'Result', 'Task']

from raisin.encapsulation.packaging import Argument, Function, Result, Task
