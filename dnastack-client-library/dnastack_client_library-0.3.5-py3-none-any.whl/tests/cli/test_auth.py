import os
import threading
import unittest
import warnings

from click.testing import CliRunner
import json
import csv
from io import StringIO
from dnastack import __main__ as dnastack_cli
from dnastack.constants import auth_scopes, default_auth
import jwt

from .utils import *
from .. import *
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from time import sleep, time


class TestCliAuthCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.data_connect_url = TEST_DATA_CONNECT_URI
        self.collections_url = TEST_COLLECTIONS_URI
        self.wallet_url = TEST_AUTH_PARAMS["publisher"]["url"]

        clear_config()
        set_cli_config(self.runner, "data_connect.url", self.data_connect_url)
        set_cli_config(self.runner, "collections.url", self.collections_url)
        set_auth_params_for_service(
            self.runner,
            service="data_connect",
            auth_params=TEST_AUTH_PARAMS["publisher"],
        )
        set_auth_params_for_service(
            self.runner,
            service="collections",
            auth_params=TEST_AUTH_PARAMS["publisher"],
        )
        set_cli_config(
            self.runner,
            f"oauth|{self.wallet_url}|scope",
            TEST_AUTH_SCOPES["publisher"],
            delimiter="|",
        )
        login_with_refresh_token_for_service(
            self.runner, "data-connect", TEST_WALLET_REFRESH_TOKEN["publisher"]
        )
        login_with_refresh_token_for_service(
            self.runner, "collections", TEST_WALLET_REFRESH_TOKEN["publisher"]
        )

    @staticmethod
    def do_login_steps(proc, auth_test, allow=True):
        # wait for device code url
        retries = 5
        while True:
            device_code_url = proc.stdout.readline().decode("utf-8")
            if device_code_url:
                break
            elif retries == 0:
                raise Exception()
            sleep(1)
            retries -= 1

        auth_test.assertIsNotNone(device_code_url)

        # make sure the browser is opened in headless mode
        chrome_options = Options()
        chrome_options.headless = True
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(device_code_url)

        driver.execute_script(
            (
                f"document.querySelector('form[name=\"token\"] input[name=\"token\"]').value = '{TEST_WALLET_PERSONAL_ACCESS_TOKEN_DNASTACK}';"
                f"document.querySelector('form[name=\"token\"] input[name=\"email\"]').value = '{TEST_WALLET_EMAIL}';"
            )
        )
        token_form = driver.find_element_by_css_selector("form[name='token']")
        token_form.submit()

        sleep(2)

        driver.find_element_by_id("continue-btn").click()

        if allow:
            driver.find_element_by_id("allow-btn").click()
        else:
            driver.find_element_by_id("deny-btn").click()

        driver.quit()

    def test_login(self):
        proc = subprocess.Popen(
            [
                "python3",
                "-m",
                "dnastack",
                "auth",
                "login",
                "data-connect",
                "--no-browser",
            ],
            stdout=subprocess.PIPE,
        )

        login_thread = threading.Thread(
            target=self.do_login_steps,
            args=(
                proc,
                self,
            ),
        )
        login_thread.start()

        login_thread.join()
        proc.wait(timeout=20)
        output, error = proc.communicate()
        exit_code = proc.returncode

        self.assertEqual(
            exit_code,
            0,
            msg=f"Login failed with output: {output.decode('utf-8')} (exit code {exit_code})",
        )
        self.assertIn("login successful", output.decode("utf-8").lower())

        self.assertIsNotNone(
            get_cli_config(self.runner, f"oauth|{self.wallet_url}", delimiter="|")
        )
        token = json.loads(
            get_cli_config(self.runner, f"oauth|{self.wallet_url}", delimiter="|")
        )

        assert_has_property(self, token, "access_token")
        self.access_token = token["access_token"]

        assert_has_property(self, token, "refresh_token")
        self.refresh_token = token["refresh_token"]

        access_jwt = jwt.decode(self.access_token, options={"verify_signature": False})
        self.assertEqual(access_jwt["tokenKind"], "bearer")
        jwt_scopes = access_jwt["scope"].split(" ")
        for scope in TEST_AUTH_SCOPES["publisher"].split():
            self.assertIn(scope, jwt_scopes)
        self.assertEqual(
            access_jwt["azp"], TEST_AUTH_PARAMS["publisher"]["client"]["id"]
        )
        self.assertEqual(f"{access_jwt['iss']}/", TEST_AUTH_PARAMS["publisher"]["url"])
        self.assertGreater(access_jwt["exp"], time())

    def test_login_no_config(self):
        clear_config()
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            ["auth", "login", "data-connect"],
        )

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn(
            "[data_connect.wallet] configuration variable is not set",
            result.output.lower(),
        )

    def test_login_deny(self):
        proc = subprocess.Popen(
            [
                "python3",
                "-m",
                "dnastack",
                "auth",
                "login",
                "data-connect",
                "--no-browser",
            ],
            stdout=subprocess.PIPE,
        )

        login_thread = threading.Thread(
            target=self.do_login_steps,
            args=(proc, self, False),
            name="login",
        )
        login_thread.start()

        login_thread.join()
        proc.wait(timeout=5)
        output, err = proc.communicate()

        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("login failed", output.decode("utf-8").lower())
        self.assertIn("access denied", output.decode("utf-8").lower())

    def test_refresh(self):
        old_token = json.loads(
            get_cli_config(self.runner, f"oauth|{self.wallet_url}", delimiter="|")
        )

        result = self.runner.invoke(
            dnastack_cli.dnastack,
            ["auth", "refresh", "data-connect"],
        )

        self.assertEqual(result.exit_code, 0)

        # make sure the access_token has changed
        new_token = json.loads(
            get_cli_config(self.runner, f"oauth|{self.wallet_url}", delimiter="|")
        )
        self.assertNotEqual(old_token["access_token"], new_token["access_token"])

    def test_refresh_token_missing_token(self):
        wallet_url = get_cli_config(self.runner, "data_connect.wallet.url")
        set_cli_config(
            self.runner, f"oauth|{wallet_url}|access_token", "", delimiter="|"
        )
        set_cli_config(
            self.runner, f"oauth|{wallet_url}|refresh_token", "", delimiter="|"
        )

        result = self.runner.invoke(
            dnastack_cli.dnastack,
            ["auth", "refresh", "data-connect"],
        )

        self.assertNotEqual(
            result.exit_code,
            0,
            msg=(
                f"'auth refresh' with no token did not fail as expected."
                f" output: {result.output}"
                f" exit code: {result.exit_code}"
            ),
        )
        self.assertIn("The refresh token does not exist", result.output)

    def test_refresh_token_bad_token(self):
        wallet_url = get_cli_config(self.runner, "data_connect.wallet.url")
        set_cli_config(
            self.runner, f"oauth|{wallet_url}|access_token", "", delimiter="|"
        )
        set_cli_config(
            self.runner, f"oauth|{wallet_url}|refresh_token", "badtoken", delimiter="|"
        )
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            ["auth", "refresh", "data-connect"],
        )

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Unable to refresh token", result.output)
