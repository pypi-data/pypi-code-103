# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2020
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import hashlib

import numpy as np
from ibm_wos_utils.drift.batch.util.constants import (RANGE_BUFFER_CONSTANT,
                                                      ConstraintName)


def get_constraint_id(constraint_name: ConstraintName, columns: list):
    """Returns Constraint ID. It is a hash of constraint name + column names
    in lower case sorted alphabetically.

    Arguments:
        constraint_name {ConstraintName} -- Constraint Name
        columns {list} -- List of column names

    Returns:
        str -- constraint id
    """
    return hashlib.sha224(bytes(",".join(
        [constraint_name.value] + sorted(map(lambda x: x.lower(), columns))), "utf-8")).hexdigest()


def get_limits_with_buffer(col_min, col_max):
    buffer = RANGE_BUFFER_CONSTANT * (col_max - col_min)

    # If both col_min and col_max are integers, bump up the buffer to
    # the next integer
    if np.issubdtype(
            type(col_min),
            np.integer) and np.issubdtype(
            type(col_max),
            np.integer):
        buffer = np.ceil(buffer).astype(int)

    return col_min - buffer, col_max + buffer


def get_primitive_value(num):
    """Get the python numeric primitive value from numpy/python numeric values"""
    if type(num) in (int, float):
        return num

    return num.item()
