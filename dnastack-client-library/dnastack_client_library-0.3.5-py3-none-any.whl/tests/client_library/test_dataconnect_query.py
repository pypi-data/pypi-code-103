import os
import unittest
from dnastack import PublisherClient, ServiceType
from .. import *


def assert_has_property(self, obj, attribute):
    self.assertTrue(
        attribute in obj,
        msg="obj lacking an attribute. obj: %s, intendedAttribute: %s"
        % (obj, attribute),
    )


class TestClientLibraryDataConnectQueryCommand(unittest.TestCase):
    def setUp(self):
        self.publisher_client = PublisherClient(
            email=TEST_WALLET_EMAIL,
            personal_access_token=TEST_WALLET_PERSONAL_ACCESS_TOKEN_PUBLISHER,
            dataconnect_url=TEST_DATA_CONNECT_URI,
        )

        self.publisher_client.auth.set_refresh_token_for_service(
            service_type=ServiceType.DATACONNECT,
            token=TEST_WALLET_REFRESH_TOKEN["publisher"],
        )
        self.publisher_client.auth.oauth[TEST_AUTH_PARAMS["publisher"]["url"]][
            "scope"
        ] = TEST_AUTH_SCOPES["publisher"]
        self.publisher_client.auth.login_for_service(service=ServiceType.DATACONNECT)

    def test_variant_query(self):
        result = self.publisher_client.dataconnect.query(
            f"SELECT * FROM {TEST_DATA_CONNECT_VARIANTS_TABLE} LIMIT 10"
        )
        self.assertIsNotNone(result)

        for item in result:
            assert_has_property(self, item, "start_position")
            assert_has_property(self, item, "end_position")
            assert_has_property(self, item, "reference_bases")
            assert_has_property(self, item, "alternate_bases")
            assert_has_property(self, item, "sequence_accession")

    def test_drs_url_query(self):
        result = self.publisher_client.dataconnect.query(
            f"SELECT drs_url FROM {TEST_DATA_CONNECT_FILES_TABLE} LIMIT 10"
        )
        self.assertIsNotNone(result)

        for item in result:
            assert_has_property(self, item, "drs_url")

    def test_incorrect_column_query(self):
        with self.assertRaises(Exception) as cm:
            self.publisher_client.dataconnect.query(
                f"SELECT invalid_column FROM {TEST_DATA_CONNECT_VARIANTS_TABLE} LIMIT 10"
            )

    def test_broken_query(self):
        with self.assertRaises(Exception) as cm:
            self.publisher_client.dataconnect.query("broken_query")
