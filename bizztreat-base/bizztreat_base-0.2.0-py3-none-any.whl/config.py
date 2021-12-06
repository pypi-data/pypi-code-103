"""Set of helpers to get config and verify it.
"""

import os
import json
import logging
from argparse import ArgumentParser
from typing import Callable, Dict, Optional

import jsonschema

logger = logging.getLogger(__name__)


def create_default_parser(guess_kbc: bool = True) -> ArgumentParser:
    """Create argument parser instance and return it.

    Keyword Arguments:
        guess_kbc {bool} -- If True, parser will try to guess whether
                            we are running in KBC or Bizzflow (default: {True})

    Returns:
        ArgumentParser -- Argument parser object ready to parse input arguments
    """
    parser = ArgumentParser()
    if not guess_kbc:
        is_kbc = False
    else:
        is_kbc = os.path.exists("/data/config.json")
    if is_kbc:
        config_default = "/data/config.json"
    else:
        config_default = "/config/config.json"
    parser.add_argument("--kbc-mode", action="store_true", default=is_kbc, help="Run in KBC mode")
    parser.add_argument("--output", action="store", default="/data/out/tables", help="Output directory for files")
    parser.add_argument("--input", action="store", default="/data/in/tables", help="Input directory for files")
    parser.add_argument("--config", action="store", default=config_default, help="Config location")
    parser.add_argument(
        "--config-schema", action="store", default="./config.schema.json", help="Config schema location"
    )
    return parser


class Config:
    """Helper class to get component configuration"""

    def __init__(
        self, *, force_schema: bool = False, parser_factory: Callable[[], ArgumentParser] = create_default_parser
    ):
        self.parser = parser_factory()
        self.args = self.parser.parse_args()
        self.force_schema = force_schema
        self.config = self.read_config()
        self.output_folder = self.args.output
        self.input_folder = self.args.input
        try:
            self.schema_valid = self.verify_config()
        except FileNotFoundError as error:
            if force_schema:
                raise FileNotFoundError("Schema for config was not provided by the component") from error
            self.schema_valid = False

    def read_config(self, config_path: Optional[str] = None) -> Dict:
        """Read config from either the default location or specified `config_path` and return it as a Python dict

        Keyword Arguments:
            config_path {Optional[str]} -- Override config location (default: {None})

        Raises:
            ValueError: If no config file was specified, neither default exists
            FileNotFoundError: File was specified but does not exist

        Returns:
            Dict -- [description]
        """
        config_path = config_path or self.args.config
        if config_path is None:
            raise ValueError("No config path was specified")

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file was not found in {config_path}")

        with open(config_path, "r", encoding="utf-8") as fid:
            content = json.load(fid)

        if self.args.kbc_mode:
            return content.get("parameters", {})
        return content

    def verify_config(self, config: Optional[Dict] = None) -> bool:
        """Verify either previously read config or an overridden `config`.

        Keyword Arguments:
            config {Optional[Dict]} -- Override previously read config with this one (default: {None})

        Raises:
            ValueError: No config was specified, nor it was previously read
            FileNotFoundError: Schema does not exist

        Returns:
            bool -- True if config checks out, False if it does not
        """
        config = config or self.config
        if config is None:
            raise ValueError("No config was specified")

        if not os.path.exists(self.args.config_schema):
            raise FileNotFoundError(f"Configuration schema was not found in {self.args.config_schema}")

        with open(self.args.config_schema, "r", encoding="utf-8") as fid:
            schema = json.load(fid)

        try:
            jsonschema.validate(instance=config, schema=schema)
        except jsonschema.ValidationError as error:
            if self.force_schema:
                raise error
            logger.error("Configuration failed validation")
            logger.error(error)
            return False
        return True

    def __getitem__(self, key):
        return self.config[key]

    def get(self, key, default=None):
        return self.config.get(key, default)
