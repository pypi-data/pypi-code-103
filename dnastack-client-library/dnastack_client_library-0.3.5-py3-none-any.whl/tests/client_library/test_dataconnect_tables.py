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


class TestClientLibraryDataConnectTablesCommand(unittest.TestCase):
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

    def test_tables_list(self):
        result = self.publisher_client.dataconnect.list_tables()

        self.assertIsNotNone(result)

        for item in result:
            assert_has_property(self, item, "name")
            assert_has_property(self, item, "data_model")
            assert_has_property(self, item["data_model"], "$ref")

    def test_tables_get_table(self):
        get_table_result = self.publisher_client.dataconnect.get_table(
            TEST_DATA_CONNECT_VARIANTS_TABLE
        )

        self.assertIsNotNone(get_table_result)

        assert_has_property(self, get_table_result, "name")
        assert_has_property(self, get_table_result, "description")
        assert_has_property(self, get_table_result, "data_model")
        assert_has_property(self, get_table_result["data_model"], "$id")
        assert_has_property(self, get_table_result["data_model"], "$schema")
        assert_has_property(self, get_table_result["data_model"], "description")

        for property in get_table_result["data_model"]["properties"]:
            assert_has_property(
                self, get_table_result["data_model"]["properties"][property], "format"
            )
            assert_has_property(
                self, get_table_result["data_model"]["properties"][property], "type"
            )
            assert_has_property(
                self,
                get_table_result["data_model"]["properties"][property],
                "$comment",
            )

    def test_tables_get_table_does_not_exist(self):
        with self.assertRaises(Exception) as cm:
            self.publisher_client.dataconnect.get_table("some table name")
