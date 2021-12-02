import os
import unittest
from dnastack import PublisherClient, ServiceType
from .. import *


class TestCliAuthCommand(unittest.TestCase):
    def setUp(self):
        self.publisher_client = PublisherClient(
            email=TEST_WALLET_EMAIL,
            personal_access_token=TEST_WALLET_PERSONAL_ACCESS_TOKEN_PUBLISHER,
            dataconnect_url=TEST_DATA_CONNECT_URI,
            collections_url=TEST_COLLECTIONS_URI,
        )

    def test_login(self):
        self.publisher_client.auth.login_for_service(ServiceType.DATACONNECT)
        self.assertIsNotNone(
            self.publisher_client.auth.oauth[
                self.publisher_client.dataconnect.auth_params["url"]
            ]
        )

    def test_login_bad_credentials(self):
        self.publisher_client.personal_access_token = "badtoken"
        with self.assertRaises(Exception) as ctx:
            self.publisher_client.auth.login_for_service(ServiceType.DATACONNECT)
            self.assertIsNotNone(ctx.exception.message)
            self.assertIn(
                "The personal access token and/or email provided is invalid",
                ctx.exception.message,
            )

    def test_login_bad_drs_server(self):
        with self.assertRaises(Exception) as ctx:
            self.publisher_client.auth.login_for_drs(drs_server="badserver")
            self.assertIsNotNone(ctx.exception.message)
            self.assertIn("The authorization failed", ctx.exception.message)

    def test_refresh_token(self):
        # first we must clear the existing token and replace with just a refresh_token
        self.publisher_client.auth.oauth[
            self.publisher_client.dataconnect.get_wallet_url()
        ] = {}
        self.publisher_client.auth.set_refresh_token_for_service(
            service_type=ServiceType.DATACONNECT,
            token=TEST_WALLET_REFRESH_TOKEN["publisher"],
        )

        self.publisher_client.auth.refresh_token_for_service(
            service_type=ServiceType.DATACONNECT
        )

        self.assertIsNotNone(self.publisher_client.dataconnect.get_client_oauth_token())
        self.assertIsNotNone(
            self.publisher_client.dataconnect.get_client_oauth_token()["access_token"]
        )
        self.assertIsNotNone(
            self.publisher_client.dataconnect.get_client_oauth_token()["refresh_token"]
        )

    def test_refresh_token_missing_token(self):
        with self.assertRaises(Exception) as ctx:
            self.publisher_client.auth.oauth[
                self.publisher_client.dataconnect.get_wallet_url()
            ] = {}
            self.publisher_client.auth.refresh_token_for_service(
                service_type=ServiceType.DATACONNECT
            )

            self.assertIsNotNone(ctx.exception.message)
            self.assertIn(
                "There is no refresh token configured.", ctx.exception.message
            )

    def test_refresh_token_bad_token(self):
        with self.assertRaises(Exception) as ctx:
            self.publisher_client.auth.oauth[
                self.publisher_client.dataconnect.get_wallet_url()
            ] = {}
            self.publisher_client.auth.set_refresh_token_for_service(
                service_type=ServiceType.DATACONNECT, token="badrefresh"
            )

            self.publisher_client.auth.refresh_token_for_service(
                service_type=ServiceType.DATACONNECT
            )

            self.assertIsNotNone(ctx.exception.message)
            self.assertIn(
                "There is no refresh token configured.", ctx.exception.message
            )
