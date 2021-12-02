import sys
from urllib.parse import urlunparse, urlparse
from typing import Any, Union, List

import click
import yaml
from ..constants import (
    config_file_path,
    ACCEPTED_CONFIG_KEYS,
    default_auth,
    SUPPORTED_SERVICES,
    ACCEPTED_OAUTH_KEYS,
)


# GETTERS
def get_config(
    ctx: click.Context,
    var_path: Union[list, str],
    raise_error: bool = True,
    delimiter: str = ".",
    default: Any = None,
) -> Any:
    if type(var_path) == str:
        var_path = var_path.split(delimiter)

    format_var_path(var_path)

    try:
        obj = ctx.obj
        for key in var_path:
            obj = obj[key]
    except KeyError as k:
        if raise_error:
            raise Exception(
                f"The [{delimiter.join(var_path)}] configuration variable is not set. "
                f"Run dnastack config set {delimiter.join(var_path)} [{var_path[-1].upper()}] to configure it"
            )
        else:
            return default

    if raise_error and type(obj) != get_type_of_config(var_path):
        raise Exception(
            f"Expected type [{get_type_of_config(var_path)}] for config variable "
            f"[{'.'.join(var_path)}], got [{type(obj).__name__}]"
        )

    # for the last object we don't error if it's not there, just return None
    return obj


# SETTERS
def set_config(ctx: click.Context, var_path: Union[list, str], value: Any) -> None:
    if type(var_path) == str:
        var_path = var_path.split(".")

    assert len(var_path) >= 1

    # standardize the url in the path and value to use a trailing slash
    format_var_path(var_path)
    if is_url(value):
        value = format_url_for_config(value)

    set_config_obj(ctx.obj, var_path, value)
    save_config_to_file(ctx)


def set_config_obj(obj: dict, var_path: list, value: Any) -> None:

    var_name = var_path[0]
    if var_name not in obj.keys():
        obj[var_name] = None

    if len(var_path) == 1:
        obj[var_name] = value
    else:
        if obj[var_name] is not None:
            assert type(obj[var_name]) == dict
            set_config_obj(obj[var_name], var_path[1:], value)
        else:
            obj[var_name] = {}
            set_config_obj(obj[var_name], var_path[1:], value)


# HELPERS
def is_accepted_key(var_path: List[str]) -> bool:
    obj = ACCEPTED_CONFIG_KEYS

    # since wallet servers can really be anything, we only check if the key following "oauth"
    # is a proper url, and whether the third is a valid oauth key
    if var_path[0] == "oauth":

        if len(var_path) > 3:
            return False

        # if they define which token, check if it's a valid url
        if len(var_path) > 1:
            wallet_url_info = urlparse(var_path[1])
            if not (wallet_url_info.scheme == "https" and wallet_url_info.netloc):
                return False

        # if they look for a specific value within a token, make sure it's a valid value
        if len(var_path) > 2:
            oauth_key = var_path[2]
            if oauth_key not in ACCEPTED_OAUTH_KEYS.keys():
                return False

        return True

    try:
        for var in var_path:
            obj = obj[var]
    except KeyError as k:
        return False
    return True


def get_type_of_config(var_path: list) -> type:
    obj = ACCEPTED_CONFIG_KEYS

    # since we don't know what the middle key is for "oauth"
    # we return a dictionary if it's asking for the middle key,
    # and rely on the accepted_oauth_keys for if it's asking for a value inside a oauth token
    if var_path[0] == "oauth":
        if len(var_path) == 2:
            return dict
        elif len(var_path) == 3:
            return ACCEPTED_OAUTH_KEYS.get(var_path[2])
        else:
            return type(None)

    try:
        for var in var_path:
            obj = obj.get(var)

            if obj is None:
                return type(None)

        # in the case where we don't reach an end value, we return dict
        if type(obj) == dict:
            return dict

        return obj
    except Exception as e:
        return type(None)


def get_auth_params(
    ctx: click.Context, service: str, use_default: bool = False
) -> dict:
    service = service.replace("-", "_")
    try:
        wallet = get_config(ctx, var_path=[service, "wallet"])
    except Exception as e:
        if use_default:
            wallet = default_auth
        else:
            raise e

    return wallet


def get_audience_for_wallet(ctx: click.Context, wallet_url: str) -> list:
    urls = []
    for service in SUPPORTED_SERVICES:

        if (
            get_config(
                ctx,
                var_path=[service.replace("-", "_"), "wallet", "url"],
                raise_error=False,
            )
            == wallet_url
        ):
            urls.append(
                get_config(
                    ctx, var_path=[service.replace("-", "_"), "url"], raise_error=False
                )
            )
    return urls


def save_config_to_file(ctx: click.Context):
    with open(config_file_path, "w") as config_file:
        yaml.dump(ctx.obj, config_file)


# CLICK EXTENSIONS
class APIUrl(click.ParamType):
    name = "API Url"

    def convert(self, value, param, ctx):
        pass


# Misc Helpers:


def is_url(val: Any) -> bool:
    if type(val) is not str:
        return False
    parsed_url = urlparse(val)
    return parsed_url.scheme == "https" and parsed_url.netloc


def format_url_for_config(url: str) -> str:
    parsed_url = urlparse(url)
    new_path = "/"
    if not (parsed_url.path == "" or parsed_url == "/"):
        if parsed_url.path[-1] == "/":
            new_path = parsed_url.path
        else:
            new_path = parsed_url.path + "/"
    return str(urlunparse((parsed_url.scheme, parsed_url.netloc, new_path, "", "", "")))


def format_var_path(var_path: list) -> None:
    for i in range(len(var_path)):
        if is_url(var_path[i]):
            var_path[i] = format_url_for_config(var_path[i])
