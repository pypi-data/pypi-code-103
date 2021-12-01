import logging
import os
from pydantic import Field
from pydantic import BaseSettings as PydanticBaseSettings

from .vault_helper import vault_config_settings_source


logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s:%(asctime)s:%(message)s")


class Settings(PydanticBaseSettings):
    class Config:
        vault_kubernetes_role: str = "app-role"
        vault_port: str = "8200"
        env_file_encoding = "utf-8"

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return (
                vault_config_settings_source,
                env_settings,
                file_secret_settings,
            )
