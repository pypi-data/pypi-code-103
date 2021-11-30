# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
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

def check_user_override(
    column_names:list, constraint_kind:str, user_overrides:list):

    learn_distribution_constraint = True
    learn_range_constraint = True

    if not user_overrides:
        return learn_distribution_constraint, learn_range_constraint

    column_names = [x.upper() for x in column_names]
    input_constraint_kind = "single" if constraint_kind == "single_column" else "double"

    # iterate over configs provided by user and check if given input is one of them
    for config in user_overrides:
        # find the config user has overridden and return distribution and range constraint overrides if any
        config_constraint_kind = config.get("constraint_type")
        if config_constraint_kind != input_constraint_kind:
            continue

        config_features = config.get("features")

        if config_constraint_kind == "single":
            # convert all features to upper-case
            config_features = [x.upper() for x in config_features]

            # check if given column name is part of this config's features
            if set(column_names).issubset(set(config_features)):
                # found config
                # return values for "learn_distribution_constraint" and "learn_range_constraint"
                learn_distribution_constraint = config.get("learn_distribution_constraint")
                learn_range_constraint = config.get("learn_range_constraint")
                break

        if config_constraint_kind == "double":
            # sort input column names
            column_names.sort()

            # iterate over this config's feature pairs and identify if given input column(s) are part of it.
            for feature_pair in config_features:
                feature_pair = [x.upper() for x in feature_pair]
                feature_pair.sort()

                if len(feature_pair) == 1:
                    # single value means override is applicable to all constraints where this column is present
                    if set(feature_pair).issubset(set(column_names)):
                        learn_distribution_constraint = config.get("learn_distribution_constraint")
                        learn_range_constraint = config.get("learn_range_constraint")
                        break

                if column_names == feature_pair:
                    # found config
                    # return values for "learn_distribution_constraint" and "learn_range_constraint"
                    learn_distribution_constraint = config.get("learn_distribution_constraint")
                    learn_range_constraint = config.get("learn_range_constraint")
                    break


    learn_distribution_constraint = True \
        if learn_distribution_constraint is None or learn_distribution_constraint == True else False
    learn_range_constraint = True \
        if learn_range_constraint is None or learn_range_constraint == True else False

    return learn_distribution_constraint, learn_range_constraint