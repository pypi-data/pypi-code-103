import logging
from pathlib import Path

from typing import Tuple, TypeVar, Type, Dict
from os import environ as env

from pydantic import BaseSettings

log_level = getattr(
    logging, env.get("FACT_EXPLORER_LOG_LEVEL", "WARNING").upper(), 30
)  # Setting a default here is pretty defensive. Anyhow nothing lost by doing it

log = logging.getLogger()
log.setLevel(log_level)

C = TypeVar("C", bound="Configuration.Config")


class Configuration(BaseSettings):
    database_password: str
    cryptoshred_init_vector_path: str
    database_user: str = "rdssystem"
    database_host: str = "localhost"
    database_port: str = "5432"
    database_name: str = "postgres"

    class Config:
        env_file_encoding = "utf-8"

        @classmethod
        def customize_sources(
            cls: Type[C],
            init_settings: Dict,
            env_settings: Dict,
            file_secret_settings: Dict,
        ) -> Tuple[Dict, Dict, Dict]:
            return (env_settings, init_settings, file_secret_settings)


def get_configuration(
    profile: str = "default",
    *,
    config_dir: Path = Path.home().joinpath(".fact_explorer"),
) -> Configuration:
    log.info("Getting Configuration")

    if profile:
        env_file_location = config_dir.joinpath(f"{profile}.env").absolute()
        return Configuration(_env_file=env_file_location)

    return Configuration()
