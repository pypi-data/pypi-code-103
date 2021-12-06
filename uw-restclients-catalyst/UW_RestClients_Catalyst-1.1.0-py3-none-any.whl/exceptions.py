# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Contains custom exceptions used by the catalyst rest client.
"""


class InvalidGradebookID(Exception):
    """Exception for invalid gradebook id."""
    pass


class InvalidSurveyID(Exception):
    """Exception for invalid survey id."""
    pass
