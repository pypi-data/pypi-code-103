from io import StringIO
from unittest import mock
import unittest
from unittest.mock import Mock, patch

import pandas
from requests.models import Response

from canalyst_candas import settings

from canalyst_candas.utils import (
    LogFile,
    CsvDataKeys,
    get_data_set_from_mds,
    get_forecast_url,
    _get_data_set_csv_url,
)


class BaseUtilsTests:
    """
    General test cases for the utils file
    """

    def test_get_forecast_url(self):
        # below URL should actually be valid if you want to manually test
        expected_url = f"{settings.MDS_HOST}/api/equity-model-series/S1TQ5V0161/equity-models/Q3-2021.20/forecast-periods/"
        returned_url = get_forecast_url("S1TQ5V0161", "Q3-2021.20")

        assert expected_url == returned_url


class MdsBulkDataUtilsTests(unittest.TestCase):
    """
    Test cases for the get_data_set_from_mds() method and associated methods
    """

    def setUp(self) -> None:
        self.url = f"{settings.MDS_HOST}/api/candas-csv-data/{CsvDataKeys.HISTORICAL_DATA.value}/10273/"
        self.url_candidates = [
            f"{settings.MDS_HOST}/api/candas-csv-data/forecast-data/10274/",
            self.url,
            f"{settings.MDS_HOST}/api/candas-csv-data/name-index/10269/",
            f"{settings.MDS_HOST}/api/candas-csv-data/model-info/10268/",
        ]
        self.mock_log = Mock(spec=LogFile)

        self.mock_get_data_set_urls_from_mds = patch(
            "canalyst_candas.utils._get_data_set_urls_from_mds"
        ).start()
        self.mock_get_request = patch("canalyst_candas.utils.get_request").start()

    def tearDown(self):
        patch.stopall()

    def test_get_data_set_from_mds_success(self):
        some_csv_file = '"header1", "header2", "header3"\n "data1", "data2", "data3"'
        get_csv_response = Response()
        type(get_csv_response).content = mock.PropertyMock(
            return_value=bytes(some_csv_file, "utf-8")
        )

        self.mock_get_request.return_value = get_csv_response
        self.mock_get_data_set_urls_from_mds.return_value = self.url_candidates

        result = get_data_set_from_mds(
            CsvDataKeys.HISTORICAL_DATA,
            "ABCDE12345",
            "Q1-2021.20",
            {},
            self.mock_log,
            "mds_host",
        )

        self.assertEqual(
            result.to_string(), pandas.read_csv(StringIO(some_csv_file)).to_string()
        )

    def test_get_data_set_from_mds_url_is_null(self):
        self.mock_get_data_set_urls_from_mds.return_value = []

        result = get_data_set_from_mds(
            CsvDataKeys.HISTORICAL_DATA,
            "ABCDE12345",
            "Q1-2021.20",
            {},
            self.mock_log,
            "mds_host",
        )

        self.assertIsNone(result)
        self.mock_log.write.assert_called_once_with(
            f"Candas: Error with retrieving the '{CsvDataKeys.HISTORICAL_DATA.value}' URL from the list '[]'."
        )

    def test_get_data_set_csv_url_success(self):
        result = _get_data_set_csv_url(
            self.url_candidates, CsvDataKeys.HISTORICAL_DATA.value, self.mock_log
        )
        self.assertEqual(result, self.url)

    def test_get_data_set_csv_url_data_set_is_empty(self):
        result = _get_data_set_csv_url(
            [], CsvDataKeys.HISTORICAL_DATA.value, self.mock_log
        )
        self.assertIsNone(result)
        self.mock_log.write.assert_called_once_with(
            f"Candas: Error with retrieving the '{CsvDataKeys.HISTORICAL_DATA.value}' URL from the list '[]'."
        )

    def test_get_data_set_csv_url_multiple_matches(self):
        expected_result = self.url
        url_candidates = [
            f"{settings.MDS_HOST}/api/candas-csv-data/forecast-data/10274/",
            expected_result,
            f"{settings.MDS_HOST}/api/candas-csv-data/name-index/10269/",
            f"{settings.MDS_HOST}/api/candas-csv-data/model-info/10268/",
            expected_result,
        ]

        result = _get_data_set_csv_url(
            url_candidates,
            CsvDataKeys.HISTORICAL_DATA.value,
            self.mock_log,
        )

        self.assertIsNone(result)
        self.mock_log.write.assert_called_once_with(
            f"Candas: Error with retrieving the '{CsvDataKeys.HISTORICAL_DATA.value}' URL from the list '{url_candidates}'."
        )
