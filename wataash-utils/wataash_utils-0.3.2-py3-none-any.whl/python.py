# SPDX-License-Identifier: Apache-2.0

import inspect
import os
import sys


def python_path_insert_head(directory: str):
    # if directory in sys.path:
    #     sys.path.remove(directory)
    sys.path.insert(0, directory)


def python_path_insert_head_current():
    stack = inspect.stack()
    python_path_insert_head(os.path.dirname(stack[1].filename))
