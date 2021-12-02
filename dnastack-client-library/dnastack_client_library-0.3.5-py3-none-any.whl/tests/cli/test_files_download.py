import unittest
from click.testing import CliRunner
import pathlib
from dnastack import __main__ as dnastack_cli
import glob

from .utils import set_cli_config
from .. import *


class TestCliFilesCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.data_connect_url = TEST_DATA_CONNECT_URI

        set_cli_config(self.runner, "data_connect.url", self.data_connect_url)

    def test_drs_download(self):
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            [
                "files",
                "download",
                TEST_DRS_WITH_ACCESS_URL,
                "-o",
                "out",
            ],
        )
        self.assertEqual(
            result.exit_code,
            0,
            f"'files download [{TEST_DRS_WITH_ACCESS_URL}]' for resource with access URL failed "
            f"with code {result.exit_code}: {result.output}",
        )

        self.assertTrue(
            pathlib.Path(
                f"{os.getcwd()}/out/{TEST_DRS[TEST_DRS_WITH_ACCESS_URL]}"
            ).exists()
        )

        # clean up ./out directory
        if pathlib.Path(
            f"{os.getcwd()}/out/{TEST_DRS[TEST_DRS_WITH_ACCESS_URL]}"
        ).exists():
            pathlib.Path(
                f"{os.getcwd()}/out/{TEST_DRS[TEST_DRS_WITH_ACCESS_URL]}"
            ).unlink()
        pathlib.Path(f"{os.getcwd()}/out").rmdir()

    @unittest.skip(
        "Disabling test since the current test file is too large to download in a reasonable amount of time."
    )
    def test_drs_download_access_id(self):
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            [
                "files",
                "download",
                TEST_DRS_WITH_ACCESS_ID,
                "-o",
                "out",
            ],
        )
        self.assertEqual(
            result.exit_code,
            0,
            f"'files download [{TEST_DRS_WITH_ACCESS_ID}]' for resource with access ID failed "
            f"with code {result.exit_code}: {result.output}",
        )

        self.assertTrue(
            pathlib.Path(
                f"{os.getcwd()}/out/{TEST_DRS[TEST_DRS_WITH_ACCESS_ID]}"
            ).exists()
        )
        # clean up ./out directory
        if pathlib.Path(
            f"{os.getcwd()}/out/{TEST_DRS[TEST_DRS_WITH_ACCESS_ID]}"
        ).exists():
            pathlib.Path(
                f"{os.getcwd()}/out/{TEST_DRS[TEST_DRS_WITH_ACCESS_ID]}"
            ).unlink()
        pathlib.Path(f"{os.getcwd()}/out").rmdir()

    def test_multiple_drs_download(self):
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            ["files", "download"]
            + list(TEST_DRS.keys())
            + [
                "-o",
                "out",
            ],
        )

        self.assertEqual(
            result.exit_code,
            0,
            f"`dnastack files download` with multiple drs links failed with "
            f"exit code {result.exit_code}: {result.output}",
        )

        for drs_file in TEST_DRS.values():
            self.assertTrue(pathlib.Path(f"{os.getcwd()}/out/{drs_file}").exists())

        # clean up ./out directory
        for drs_file in TEST_DRS.values():
            if pathlib.Path(f"{os.getcwd()}/out/{drs_file}").exists():
                pathlib.Path(f"{os.getcwd()}/out/{drs_file}").unlink()

        pathlib.Path(f"{os.getcwd()}/out").rmdir()

    def test_input_file_flag_drs_download(self):
        with open("download_input_file.txt", "w") as input_file:
            # for some reason writelines doesn't add newlines so add them ourself
            input_file.writelines([f"{drs_url}\n" for drs_url in TEST_DRS.keys()])
            input_file.close()

        result = self.runner.invoke(
            dnastack_cli.dnastack,
            [
                "files",
                "download",
                "-i",
                pathlib.Path("./download_input_file.txt"),
                "-o",
                "out",
            ],
        )
        self.assertEqual(
            result.exit_code,
            0,
            f"`dnastack files download` from file failed "
            f"with exit code {result.exit_code}: {result.output}",
        )

        for drs_file in TEST_DRS.values():
            self.assertTrue(pathlib.Path(f"{os.getcwd()}/out/{drs_file}").exists())

        # clean up ./out directory
        if pathlib.Path(f"{os.getcwd()}/download_input_file.txt").exists():
            pathlib.Path(f"{os.getcwd()}/download_input_file.txt").unlink()
        for drs_file in TEST_DRS.values():
            if pathlib.Path(f"{os.getcwd()}/out/{drs_file}").exists():
                pathlib.Path(f"{os.getcwd()}/out/{drs_file}").unlink()
        pathlib.Path(f"{os.getcwd()}/out").rmdir()

    def test_drs_download_from_broken_url(self):
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            [
                "files",
                "download",
                "drs://drs.international.covidcloud.ca/072f2fb6-8240-4b1e-BROKEN-b736-7868f559c795",
                "-o",
                "out",
            ],
        )
        self.assertIn(
            "Could not get drs object id from url "
            "[drs://drs.international.covidcloud.ca/072f2fb6-8240-4b1e-BROKEN-b736-7868f559c795]",
            result.output,
        )
