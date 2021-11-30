# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
from enum import Enum


class InputDataType(Enum):
    """Supported input data types"""
    STRUCTURED = "structured"
    TEXT = "unstructured_text"
    IMAGE = "unstructured_image"


class ProblemType(Enum):
    """Supported model types"""
    BINARY = "binary"
    MULTICLASS = "multiclass"
    REGRESSION = "regression"


class ExplanationType(Enum):
    """Supported explanation types"""
    LIME = "lime"
    CONTRASTIVE = "contrastive"


class Status(Enum):
    """Enumerated type for status of the explanation."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    ERROR = "error"
    FINISHED = "finished"


class FeatureSelection(Enum):
    """Supported Feature selection values"""
    AUTO = "auto"
    FORWARD_SELECTION = "forward_selection"
    LASSO_PATH = "lasso_path"
    HIGHEST_WEIGHTS = "highest_weights"
    NONE = "none"
