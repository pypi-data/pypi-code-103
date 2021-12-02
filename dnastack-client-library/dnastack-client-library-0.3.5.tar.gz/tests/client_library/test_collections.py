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


class TestClientLibraryCollectionsCommand(unittest.TestCase):
    def setUp(self):
        self.publisher_client = PublisherClient(
            email=TEST_WALLET_EMAIL,
            personal_access_token=TEST_WALLET_PERSONAL_ACCESS_TOKEN_PUBLISHER,
            collections_url=TEST_COLLECTIONS_URI,
        )

        self.publisher_client.auth.set_refresh_token_for_service(
            service_type=ServiceType.COLLECTIONS,
            token=TEST_WALLET_REFRESH_TOKEN["publisher"],
        )
        self.publisher_client.auth.oauth[TEST_AUTH_PARAMS["publisher"]["url"]][
            "scope"
        ] = TEST_AUTH_SCOPES["publisher"]
        self.publisher_client.auth.login_for_service(service=ServiceType.COLLECTIONS)

    def test_collections_list(self):
        result_objects = self.publisher_client.collections.list()

        for item in result_objects:
            assert_has_property(self, item, "name")
            assert_has_property(self, item, "id")

    def test_collections_tables_list(self):
        result_objects = self.publisher_client.collections.list_tables(
            TEST_COLLECTION_NAME
        )

        for item in result_objects:
            assert_has_property(self, item, "name")
            assert_has_property(self, item, "data_model")
            assert_has_property(self, item["data_model"], "$ref")

    def test_collections_tables_list_bad_collection(self):
        result_objects = self.publisher_client.collections.list_tables("bad-collection")

        self.assertEqual(len(result_objects), 0)

    def test_collections_query(self):
        result_objects = self.publisher_client.collections.query(
            TEST_COLLECTION_NAME, TEST_COLLECTION_QUERY
        )

        self.assertGreater(len(result_objects), 0)

        for item in result_objects:
            assert_has_property(self, item, "start_position")
            assert_has_property(self, item, "sequence_accession")

    def test_collections_query_bad_query(self):
        with self.assertRaises(Exception):
            self.publisher_client.collections.query(
                TEST_COLLECTION_NAME, "SELECT badfield FROM badtable"
            )

    def test_collections_query_bad_collection(self):
        with self.assertRaises(Exception):
            self.publisher_client.collections.query(
                "badcollection", "SELECT badfield FROM badtable"
            )
