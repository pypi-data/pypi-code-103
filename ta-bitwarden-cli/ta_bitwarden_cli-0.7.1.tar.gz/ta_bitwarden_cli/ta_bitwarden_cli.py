import os
import subprocess
import json
import logging
import re

from retry import retry
from .download_bitwarden import DownloadBitwarden


class BitwardenServerException(Exception):
    pass


class Bitwarden(object):
    """
    Main class that does all work
    """

    def __init__(self, bitwarden_credentials=None):
        """
        bitwarden_credentials - dict with 'password' / 'client_id' / 'client_secret' keys
        'bw' binary should be already in PATH
        """
        self.data = {}
        self.path_to_exe_file = "bw"
        self.bitwarden_credentials = bitwarden_credentials
        self.session_key = ""

    def bitwarden_exe(self, *command):
        """
        Provide coma-separated command line arguments that you want to provide to bw CLI binary
        Searches binary in PATH. If fails tries to run it from current working directory
        Examples:
          - bw.bitwarden_exe('logout')
          - bw.bitwarden_exe(
            "unlock",
            self.bitwarden_credentials["password"],
            "--raw",
            )
        """
        env = {
            **os.environ,
        }

        if (
            self.bitwarden_credentials["client_id"]
            and self.bitwarden_credentials["client_secret"]
        ):
            env["BW_CLIENTID"] = str(self.bitwarden_credentials["client_id"])
            env["BW_CLIENTSECRET"] = str(self.bitwarden_credentials["client_secret"])
            logging.info("Using provided client_id and client_secret")
        else:
            logging.info("Using client_id and client_secret from env vars")

        if not env["BW_CLIENTID"] or not env["BW_CLIENTSECRET"]:
            raise Exception("Empty client_id or client_secret!")

        try:
            return subprocess.run(
                [
                    self.path_to_exe_file,
                    *command,
                ],
                capture_output=True,
                text=True,
                timeout=180,
                env=env,
            )
        except FileNotFoundError:
            self.path_to_exe_file = DownloadBitwarden.download_bitwarden()
            return subprocess.run(
                [
                    self.path_to_exe_file,
                    *command,
                ],
                capture_output=True,
                text=True,
                timeout=180,
                env=env,
            )

    @retry(BitwardenServerException, delay=5, tries=3)
    def bitwarden_login(self):
        """
        Performs login opeartion via BitWarden CLI
        Requires password / client_id / client_secret already set when creation Bitwarden instance
        """
        self.bitwarden_exe("logout")

        bitwarden_app = self.bitwarden_exe(
            "login",
            "--apikey",
        )

        if "You are logged in!" in bitwarden_app.stdout:
            bitwarden_app = self.bitwarden_exe(
                "unlock",
                self.bitwarden_credentials["password"],
                "--raw",
            )

            if "Invalid master password" in bitwarden_app.stderr:
                logging.error("STDOUT: " + bitwarden_app.stdout)
                logging.error("STDERR: " + bitwarden_app.stderr)
                raise Exception("Invalid master password!")

            if not re.search(r".{80,}", bitwarden_app.stdout):
                logging.error("STDOUT: " + bitwarden_app.stdout)
                logging.error("STDERR: " + bitwarden_app.stderr)
                raise Exception("No session key returned after login!")

            self.session_key = bitwarden_app.stdout
        else:
            logging.error("STDOUT: " + bitwarden_app.stdout)
            logging.error("STDERR: " + bitwarden_app.stderr)

            if "invalid_client" in bitwarden_app.stderr:
                raise Exception("Invalid bitwarden client_id or client_secret!")

            raise BitwardenServerException(
                "Bitwarden Server error during login! Retrying..."
            )

    def get_credentials(self, user_credentials_name):
        """
        This method is for backward compatibility
        """
        self.bitwarden_login()
        self.get_data(user_credentials_name)
        return self.data

    def get_data(self, data):
        """
        Core method
        Obtaining of data from bitwarden vault for provided Key Name
        Saves dict with results to self.data variable
        Each key in dict is your custom name
        Each value in dict is another dict with data from bitwarden vault

        Example:

          items = {
              "unicourt_api": "UniCourt API",
              "unicourt_alpha_api": "UniCourt Alpha API Dev Portal",
              "aws": "AWS Access Key & S3 Bucket",
          }
          bw.get_data(items)
          assert isinstance(bw.data['aws'],dict)
        """
        print("Sync bitwarden data...")
        bitwarden_app = self.bitwarden_exe(
            "sync",
            "--session",
            self.session_key,
        )

        print("Getting bitwarden data...")
        bitwarden_app = self.bitwarden_exe(
            "list",
            "items",
            "--session",
            self.session_key,
        )

        if not bitwarden_app.stdout:
            raise Exception("Empty items list! Probably some issue with login!")

        bitwarden_items = json.loads(bitwarden_app.stdout)
        for credentials_key, credentials_name in data.items():
            for bw_item in bitwarden_items:
                if credentials_name == bw_item["name"]:
                    self.data[credentials_key] = {}
                    self.data[credentials_key]["login"] = bw_item["login"]["username"]
                    self.data[credentials_key]["password"] = bw_item["login"][
                        "password"
                    ]
                    if "uris" in bw_item["login"]:
                        self.data[credentials_key]["url"] = bw_item["login"]["uris"][0][
                            "uri"
                        ]
                    else:
                        self.data[credentials_key]["url"] = ""
                    if bw_item["login"]["totp"] is None:
                        self.data[credentials_key]["otp"] = ""
                    else:
                        bitwarden_app = self.bitwarden_exe(
                            "get",
                            "totp",
                            bw_item["id"],
                            "--session",
                            self.session_key,
                        )
                        self.data[credentials_key]["otp"] = bitwarden_app.stdout
                    if "fields" in bw_item:
                        for field in bw_item["fields"]:
                            self.data[credentials_key][field["name"]] = field["value"]
        if len(self.data) != len(data):
            raise Exception(
                "Invalid bitwarden collection or key name or no access to collection for this user!"
            )

    def get_attachment(self, item_name: str, file_name: str, output_folder: str = os.getcwd()):
        """
        Downloads attachment file from particular item to current working directory
        Item name should be unique
        File name should be unique

        Example:

            items = {
                "test": "pypi.org",
            }
            self.bw.bitwarden_login()
            self.bw.get_attachment(items["test"], "att.txt")
            f = open("att.txt", "r")
            assert f.read() == "secret text\n"
        """
        if not isinstance(item_name, str) or not isinstance(file_name, str):
            raise Exception("item_name and file_name should be strings!")
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        # Get item ID
        bitwarden_app = self.bitwarden_exe(
            "get",
            "item",
            item_name,
            "--session",
            self.session_key,
        )

        if bitwarden_app.stderr:
            logging.error("STDOUT: " + bitwarden_app.stdout)
            logging.error("STDERR: " + bitwarden_app.stderr)
            if "More than one result was found" in bitwarden_app.stderr:
                raise Exception(
                    "More than one result for item name was found! Name should be unique!"
                )
            if "Not found" in bitwarden_app.stderr:
                raise Exception(
                    "Cannot find bitwarden item '{}'! Check the name".format(
                        str(item_name)
                    )
                )
            raise Exception("Unknown error during items obtaining!")

        bitwarden_items = json.loads(bitwarden_app.stdout)
        item_id = str(bitwarden_items["id"])

        bitwarden_app = self.bitwarden_exe(
            "get",
            "attachment",
            file_name,
            "--itemid",
            item_id,
            "--session",
            self.session_key,
            "--output",
            os.path.join(output_folder, file_name)
        )

        if bitwarden_app.stderr:
            logging.error("STDOUT: " + bitwarden_app.stdout)
            logging.error("STDERR: " + bitwarden_app.stderr)

            if "was not found" in bitwarden_app.stderr:
                raise Exception("Attachment was not found!")

            raise Exception("Unknown error during attachment downloading!")

        print("Attachment '{}' downloaded sucessfully!".format(file_name))
