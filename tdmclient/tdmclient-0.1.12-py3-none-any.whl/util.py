# This file is part of tdmclient.
# Copyright 2021 ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE,
# Miniature Mobile Robots group, Switzerland
# Author: Yves Piguet
#
# SPDX-License-Identifier: BSD-3-Clause

"""
Misc utility functions related to specific Thymio events and variables.
Author: Yves Piguet, EPFL
"""

import code
import ast
import sys
import re

from tdmclient import ClientAsync, ArrayCache
from tdmclient.atranspiler import ATranspiler
from tdmclient.module_thymio import ModuleThymio
from tdmclient.module_clock import ModuleClock


def handle_received_events(event_name, event_data):
    """Handle an event received from a node.
    Return a tuple (handled, exit, print), where handled is True if the event
    has been recognized and handled; exit is None to continue receiving more
    events, a status number if exit(status) has been executed, or a message to
    be displayed for another reason to stop; and print is a message sent by
    print to be displayed, or None.
    """

    if event_name == "_exit":
        return True, True, None
    elif event_name == "_print":
        print_id = event_data[0]
        print_format, print_num_args = print_statements[print_id]
        print_args = tuple(event_data[1 : 1 + print_num_args])
        print_str = print_format % print_args
        return True, False, print_str
    else:
        return False, False, None

def transpiler_events_to_register(transpiler):
    """Get the list of events to register before running a transpiled program.
    """

    events = []
    print_statements = transpiler.print_format_strings
    if len(print_statements) > 0:
        events.append(("_print", 1 + transpiler.print_max_num_args))
    if transpiler.has_exit_event:
        events.append(("_exit", 1))
    for event_name in transpiler.events_in:
        events.append((event_name, transpiler.events_in[event_name]))
    for event_name in transpiler.events_out:
        events.append((event_name, transpiler.events_out[event_name]))
    return events
