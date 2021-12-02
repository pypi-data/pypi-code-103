import os
import unittest
import pathlib
from dnastack import PublisherClient
from .. import *


class TestClientLibraryFilesCommand(unittest.TestCase):
    def setUp(self):
        self.publisher_client = PublisherClient(
            email=TEST_WALLET_EMAIL,
            personal_access_token=TEST_WALLET_PERSONAL_ACCESS_TOKEN_PUBLISHER,
            dataconnect_url=TEST_DATA_CONNECT_URI,
        )

    def test_drs_download(self):
        drs_url = TEST_DRS_URLS[0]
        self.publisher_client.download(urls=[drs_url], output_dir="out")
        self.assertTrue(
            pathlib.Path(f"{os.getcwd()}/out/{TEST_DRS_FILENAMES[0]}").exists()
        )

        # clean up ./out directory
        if pathlib.Path(f"{os.getcwd()}/out/{TEST_DRS_FILENAMES[0]}").exists():
            pathlib.Path(f"{os.getcwd()}/out/{TEST_DRS_FILENAMES[0]}").unlink()
        pathlib.Path(f"{os.getcwd()}/out").rmdir()

    def test_multiple_drs_download(self):
        self.publisher_client.download(urls=TEST_DRS_URLS, output_dir="out")

        for drs_file in TEST_DRS_FILENAMES:
            self.assertTrue(
                pathlib.Path(f"{os.getcwd()}/out/{drs_file}").exists(),
                f"DRS file {os.getcwd()}/out/{drs_file} does not exist",
            )

        # clean up ./out directory
        for drs_file in TEST_DRS_FILENAMES:
            if pathlib.Path(f"{os.getcwd()}/out/{drs_file}").exists():
                pathlib.Path(f"{os.getcwd()}/out/{drs_file}").unlink()

        pathlib.Path(f"{os.getcwd()}/out").rmdir()

    def test_drs_download_from_broken_url(self):
        with self.assertRaises(Exception) as cm:
            self.publisher_client.download(
                urls=[
                    "drs://drs.international.covidcloud.ca/072f2fb6-8240-4b1e-BROKEN-b736-7868f559c795"
                ]
            )

    def test_drs_load(self):
        resource_url = TEST_DRS_URLS[0]
        data = self.publisher_client.load([resource_url])

        self.assertIsNotNone(data)

    def test_drs_load_broken_url(self):
        with self.assertRaises(Exception) as cm:
            resource_url = "drs://drs.international.covidcloud.ca/f5ff16d5-6be8-425c-BROKEN-acb5-8edbf023db52"
            self.publisher_client.load([resource_url])
