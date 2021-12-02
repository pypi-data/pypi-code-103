import os

__version__ = "0.3.5"

# This is the public client wallet.publisher.dnastack.com used if the user does not set their own
default_auth = {
    "url": "https://wallet.publisher.dnastack.com/",
    "client": {
        "redirect_url": "https://wallet.publisher.dnastack.com/",
        "id": "publisher-cli",
        "secret": "WpEmHtAiB73pCrhbEyci42sBFcfmWBdj",
    },
}

cli_directory = f"{os.path.expanduser('~')}/.dnastack"
config_file_path = f"{cli_directory}/config.yaml"
downloads_directory = f"{os.getcwd()}"

# NOTE: This is not necessarily all the possible config keys, but all of the settable ones
# also include types for the config keys
ACCEPTED_CONFIG_KEYS = {
    "data_connect": {
        "url": str,
        "wallet": {
            "url": str,
            "client": {"id": str, "secret": str, "redirect_url": str},
        },
    },
    "user": {
        "personal_access_token": str,
        "email": str,
    },
    "oauth": {
        "refresh_token": str,
    },
    "collections": {
        "url": str,
        "wallet": {
            "url": str,
            "client": {"id": str, "secret": str, "redirect_url": str},
        },
    },
    "wes": {
        "url": str,
        "wallet": {
            "url": str,
            "client": {"id": str, "secret": str, "redirect_url": str},
        },
    },
}

# The configs in oauth.[SERVER].* that are settable by the user
ACCEPTED_OAUTH_KEYS = {"access_token": str, "refresh_token": str, "scope": list}

# Map old config keys to new ones
# If there isn't a perfect fit, set the value to None
DEPRECATED_CONFIG_KEYS = {
    "wes-url": "wes.url",
    "data-connect-url": "data_connect.url",
    "collections-url": "collections.url",
    "oauth_token.refresh_token": "oauth.refresh_token",
    "personal_access_token": "user.personal_access_token",
    "email": "user.email",
    "wallet-url": None,
    "client-redirect-uri": None,
    "client-id": None,
    "client-secret": None,
    "oauth_token": None,
}

SUPPORTED_SERVICES = ["wes", "collections", "data-connect"]

auth_scopes = (
    "openid "
    "offline_access "
    "drs-object:write "
    "drs-object:access "
    "dataconnect:info "
    "dataconnect:data "
    "dataconnect:query "
    "wes"
)
