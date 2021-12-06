# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interface for interacting with Catalyst WebQ Survey
"""

from uw_catalyst.exceptions import InvalidSurveyID
from uw_catalyst import get_resource
import re


def get_survey_export(survey_id, person=None):
    """
    Returns a survey exported as an .xls file
    """
    if not valid_survey_id(survey_id):
        raise InvalidSurveyID(survey_id)

    url = "/rest/webq/v2/survey/{}/export".format(survey_id)
    headers = {"Accept": "application/zip"}

    if person is not None:
        headers["X-UW-Act-as"] = person.uwnetid

    return get_resource(url, headers)


def get_survey_results(survey_id, person=None):
    """
    Returns survey result data as an .xls file
    """
    if not valid_survey_id(survey_id):
        raise InvalidSurveyID(survey_id)

    url = "/rest/webq/v2/survey/{}/responses".format(survey_id)
    headers = {"Accept": "application/vnd.ms-excel"}

    if person is not None:
        headers["X-UW-Act-as"] = person.uwnetid

    return get_resource(url, headers)


def get_survey_code_translation(survey_id, person=None):
    """
    Returns the survey code translation table as a .csv file
    """
    if not valid_survey_id(survey_id):
        raise InvalidSurveyID(survey_id)

    url = "/rest/webq/v2/survey/{}/code-translation".format(survey_id)
    headers = {"Accept": "text/csv"}

    if person is not None:
        headers["X-UW-Act-as"] = person.uwnetid

    return get_resource(url, headers)


def valid_survey_id(survey_id):
    if re.match(r"^[1-9][0-9]{,9}$", str(survey_id)):
        return True
    return False
