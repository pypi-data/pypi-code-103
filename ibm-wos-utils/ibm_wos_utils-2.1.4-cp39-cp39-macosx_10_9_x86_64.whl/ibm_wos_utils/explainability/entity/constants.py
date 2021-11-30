# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2020
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
