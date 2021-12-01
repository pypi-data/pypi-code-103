
import os

from pydantic import Field
from .settings import Settings


VAULT_PATH = "workers/odin/"


class NatsStreamingEnv(Settings):
    nats_url: str = Field(
        ..., vault_secret_path=VAULT_PATH, vault_secret_key="nats_url"
    )
    stan_cluster_id: str = Field(
        ..., vault_secret_path=VAULT_PATH, vault_secret_key="stan_cluster_name"
    )

    stan_client_id: str = Field(
        ..., env="stan_client_id", vault_secret_path=None, vault_secret_key=None
    )

    pod_name: str = Field(
        ..., env="pod_name", vault_secret_path=None, vault_secret_key=None
    )


class OrionXEnv(Settings):
    api_key: str = Field(
        ...,
        env="orionx_api_key",
        vault_secret_path=VAULT_PATH,
        vault_secret_key="orionx_api_key",
    )
    secret_key: str = Field(
        ...,
        env="orionx_api_secret",
        vault_secret_path=VAULT_PATH,
        vault_secret_key="orionx_secret_key",
    )
    api_url: str = Field(
        ...,
        env="orionx_api_url",
        vault_secret_path=None,
        vault_secret_key=None,
    )


class KrakenEnv(Settings):
    api_key: str = Field(
        ...,
        env="kraken_api_key",
        vault_secret_path=VAULT_PATH,
        vault_secret_key="kraken_api_key",
    )
    secret_key: str = Field(
        ...,
        env="kraken_secret_key",
        vault_secret_path=VAULT_PATH,
        vault_secret_key="kraken_secret_key",
    )
    api_url: str = Field(
        ...,
        env="kraken_api_url",
        vault_secret_path=None,
        vault_secret_key=None,
    )


class BinanceEnv(Settings):
    api_key: str = Field(
        ...,
        env="binance_api_key",
        vault_secret_path=VAULT_PATH,
        vault_secret_key="binance_api_key",
    )
    secret_key: str = Field(
        ...,
        env="binance_api_secret",
        vault_secret_path=VAULT_PATH,
        vault_secret_key="binance_api_secret",
    )


class MongoEnv(Settings):
    host: str = Field(
        ...,
        env="mongo_url",
        vault_secret_path=VAULT_PATH,
        vault_secret_key="mongo_url",
    )

    name: str = Field(
        ...,
        env="mongo_name",
        vault_secret_path=None,
        vault_secret_key=None,
    )


class DiscordEnv(Settings):
    url: str = Field(
        ...,
        env="discord_url",
        vault_secret_path=None,
        vault_secret_key=None,
    )


class RedisEnv(Settings):
    host: str = Field(
        ...,
        env="redis_host",
        vault_secret_path=VAULT_PATH,
        vault_secret_key="redis_host",
    )
    port: str = Field(
        ...,
        env="redis_port",
        vault_secret_path=VAULT_PATH,
        vault_secret_key="redis_port",
    )
    password: str = Field(
        ...,
        env="redis_password",
        vault_secret_path=VAULT_PATH,
        vault_secret_key="redis_password",
    )


class RecoverOrionxEnv(Settings):
    host: str = Field(
        ...,
        env="mongo_url_read",
        vault_secret_path=VAULT_PATH,
        vault_secret_key="mongo_url_head",
    )
    user_id: str = Field(
        ...,
        env="odin_user_id",
        vault_secret_path=VAULT_PATH,
        vault_secret_key="odin_user_id",
    )
    wallet_id: str = Field(
        ...,
        env="odin_wallet_id",
        vault_secret_path=VAULT_PATH,
        vault_secret_key="odin_wallet_id",
    )
