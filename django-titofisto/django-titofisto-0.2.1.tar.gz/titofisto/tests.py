from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from unittest import TestCase

from freezegun import freeze_time

from django.conf import settings
from django.test import Client

from .storage import TitofistoStorage


class TitofistoTestCase(TestCase):
    def setUp(self):
        self.storage = TitofistoStorage()

        self.test_file_1 = b"The quick brown fox jumps over the lazy dog"
        self.test_file_1_name = "quickfox.dat"
        self.storage.save(self.test_file_1_name, BytesIO(self.test_file_1))

        self.test_file_2 = b"Franz jagt im komplett verwahrlosten Taxi quer durch Bayern"
        self.test_file_2_name = "franztaxi.dat"
        self.storage.save(self.test_file_2_name, BytesIO(self.test_file_2))

        self.test_file_3 = b"Franz jagt im komplett verwahrlosten Taxi quer durch Bayern"
        self.test_file_3_name = "public/franztaxi.dat"
        self.storage.save(self.test_file_3_name, BytesIO(self.test_file_3))

        self.param = "titofisto_token"
        self.timeout = 60 * 60
        self.client = Client()

    def tearDown(self):
        self.storage.delete(self.test_file_1_name)
        self.storage.delete(self.test_file_2_name)

    def test_token_deterministic(self):
        """The generated token is deterministic for a single, unchanged file"""
        ts = int(datetime.now().strftime("%s"))

        token_1 = self.storage.get_token(self.test_file_1_name, ts)
        token_2 = self.storage.get_token(self.test_file_1_name, ts)

        self.assertEqual(token_1, token_2)

    def test_token_file_dependent(self):
        """The generated token is different for different files"""
        ts = int(datetime.now().strftime("%s"))

        token_1 = self.storage.get_token(self.test_file_1_name, ts)
        token_2 = self.storage.get_token(self.test_file_2_name, ts)

        self.assertNotEqual(token_1, token_2)

    def test_token_ts_dependent(self):
        """The generated token is different for different timestamps"""
        ts_1 = int(datetime.now().strftime("%s"))
        ts_2 = ts_1 + 5

        token_1 = self.storage.get_token(self.test_file_1_name, ts_1)
        token_2 = self.storage.get_token(self.test_file_2_name, ts_2)

        self.assertNotEqual(token_1, token_2)

    def test_get_valid_token(self):
        """A file can be retrieved with a valid token"""
        token = self.storage.get_token(self.test_file_1_name)

        url = (
            f"{settings.MEDIA_URL}{self.test_file_1_name}?"
            f"{self.param}={token}"
        )
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(list(res.streaming_content)[0], self.test_file_1)

    def test_get_invalid_token(self):
        """A file can not be retrieved with an invalid token"""
        token = self.storage.get_token(self.test_file_1_name)

        url = (
            f"{settings.MEDIA_URL}{self.test_file_1_name}?"
            f"{self.param}=a{token}"
        )
        res = self.client.get(url)

        self.assertEqual(res.status_code, 404)

    def test_get_invalid_ts(self):
        """A file can not be retrieved with an invalid timestamp"""
        token = self.storage.get_token(self.test_file_1_name)

        url = (
            f"{settings.MEDIA_URL}{self.test_file_1_name}?"
            f"{self.param}={token}a"
        )
        res = self.client.get(url)

        self.assertEqual(res.status_code, 404)

    def test_get_close_to_timeout(self):
        """A file can still be retrieved close to the timeout"""
        now = datetime.now()
        token = self.storage.get_token(self.test_file_1_name, int(now.strftime("%s")))

        url = (
            f"{settings.MEDIA_URL}{self.test_file_1_name}?"
            f"{self.param}={token}"
        )
        with freeze_time(now + timedelta(seconds=self.timeout - 1)):
            res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(list(res.streaming_content)[0], self.test_file_1)

    def test_get_after_timeout(self):
        """A file can not be retrieved after the timeout"""
        now = datetime.now()
        token = self.storage.get_token(self.test_file_1_name, int(now.strftime("%s")))

        url = (
            f"{settings.MEDIA_URL}{self.test_file_1_name}?"
            f"{self.param}={token}"
        )
        with freeze_time(now + timedelta(seconds=self.timeout + 1)):
            res = self.client.get(url)

        self.assertEqual(res.status_code, 404)

    def test_get_after_mtime_change(self):
        """A file can not be retrieved with the same token after its mtime changes"""
        now = datetime.now()
        token = self.storage.get_token(self.test_file_1_name, int(now.strftime("%s")))

        url = (
            f"{settings.MEDIA_URL}{self.test_file_1_name}?"
            f"{self.param}={token}"
        )
        with freeze_time(now + timedelta(seconds=10)):
            Path(self.storage.path(self.test_file_1_name)).touch()
        res = self.client.get(url)

        self.assertEqual(res.status_code, 404)

    def test_url(self):
        """The URL for a file should contain a token."""
        url1 = self.storage.url(self.test_file_1_name)
        url2 = self.storage.url(self.test_file_2_name)
        self.assertIn(self.param, url1)
        self.assertIn(self.param, url2)

    def test_public_files_url(self):
        """The URL for a file in the public namespace doesn't contain a token."""
        url = self.storage.url(self.test_file_3_name)
        self.assertNotIn(self.param, url)

    def test_public_files_view(self):
        """A file in the public namespace can be acessed without a token."""
        self.storage.url(self.test_file_3_name)
        url = (
            f"{settings.MEDIA_URL}{self.test_file_3_name}"
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)  