# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_pws import PWS
from uw_pws.util import fdao_pws_override
from uw_catalyst.util import fdao_catalyst_override
from uw_catalyst.survey import *
from uw_catalyst.exceptions import InvalidSurveyID
import mock


@fdao_pws_override
@fdao_catalyst_override
class CatalystTestSurvey(TestCase):
    def test_invalid_survey_id(self):
        self.assertRaises(
            InvalidSurveyID, get_survey_results, None)
        self.assertRaises(
            InvalidSurveyID, get_survey_results, '')
        self.assertRaises(
            InvalidSurveyID, get_survey_export, 'abc')
        self.assertRaises(
            InvalidSurveyID, get_survey_export, 00000)
        self.assertRaises(
            InvalidSurveyID, get_survey_code_translation, 11111111111)

    @mock.patch('uw_catalyst.survey.get_resource')
    def test_survey_export(self, mock_fn):
        person = PWS().get_person_by_netid('bill')

        response = get_survey_export(12345, person)

        mock_fn.assert_called_with('/rest/webq/v2/survey/12345/export', {
            'Accept': 'application/zip',
            'X-UW-Act-as': 'bill'})

    @mock.patch('uw_catalyst.survey.get_resource')
    def test_survey_results(self, mock_fn):
        person = PWS().get_person_by_netid('bill')

        response = get_survey_results(12345, person)

        mock_fn.assert_called_with('/rest/webq/v2/survey/12345/responses', {
            'Accept': 'application/vnd.ms-excel',
            'X-UW-Act-as': 'bill'})

    @mock.patch('uw_catalyst.survey.get_resource')
    def test_survey_code_translation(self, mock_fn):
        person = PWS().get_person_by_netid('bill')

        response = get_survey_code_translation(12345, person)

        mock_fn.assert_called_with(
            '/rest/webq/v2/survey/12345/code-translation', {
                'Accept': 'text/csv',
                'X-UW-Act-as': 'bill'})
