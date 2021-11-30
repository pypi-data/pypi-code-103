# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2020
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

"""
Contains constants used in the fairness spark jobs.
"""

BINARY_MODEL_TYPE = "binary"
MULTICLASS_MODEL_TYPE = "multiclass"
REGRESSION_MODEL_TYPE = "regression"

CATEGORICAL_DATA_TYPES = [
    "string"
]

NUMERICAL_DATA_TYPES = [
    "integer",
    "float",
    "double",
    "long"
]

GROUP_BIAS_CALCULATION_WINDOW = 7  # In days
TIMESTAMP_MODELING_ROLE = "record-timestamp"
