#
# Copyright (C) 2020 IHS Markit.
# All Rights Reserved
#
import os
from distutils.version import StrictVersion
import warnings
import requests
import logging

from dli.client.logging import _setup_logging
from dli.client.dli_client import DliClient
from dli import __version__


logger = logging.getLogger(__name__)
trace_logger = logging.getLogger('trace_logger')
DEPRECATED_AGE = 1


def _set_pypi_url(package_name):
    return f"https://pypi.org/pypi/{package_name}/json"


def _is_release(x):
    return x.replace(".", "").isnumeric()


def _version_check(package_name):
    url = _set_pypi_url(package_name)

    try:
        data = requests.get(url).json()
        versions = list(x for x in data["releases"].keys() if _is_release(x))
        versions.sort(key=StrictVersion)
        versions.reverse()

        offset = versions.index(__version__)
        if offset > DEPRECATED_AGE:
            warnings.warn("You are using an old version of the SDK, please "
                          "upgrade using `pip install dli --upgrade` "
                          "before the SDK no longer functions as expected",
                          PendingDeprecationWarning)

    except requests.exceptions.SSLError as e:
        # Version check has been see to fail by Gilberto with an SSLError
        # when doing the handshake with pypi.
        trace_logger.warning(
            f'Could not connect to pypi to check the installed DLI '
            f'version. This may be due to your internet '
            f'security rules. You can check for the latest version by '
            f'visiting https://pypi.org/project/dli/',
            extra={'SSLError': e}
        )
        pass
    except Exception:
        pass


def _start_session(
    root_url="https://catalogue.datalake.ihsmarkit.com/__api",
    debug=False,
    strict=True,
    use_keyring=True,
    log_level=None,
    show_login_url=False,
):
    if log_level is None:
        log_level = 'stderr:info'
    logger = _setup_logging(log_level)

    _version_check('dli')

    user = os.environ.get("DLI_ACCESS_KEY_ID")
    pasw = os.environ.get("DLI_SECRET_ACCESS_KEY")

    logger.debug("Checking auth flow")

    try:
        if user is not None and pasw is not None:
            logger.debug("Using SAM client credentials authentication flow")
            return get_client()(
                root_url,
                debug=debug,
                strict=strict,
                access_id=user, secret_key=pasw,
                use_keyring=use_keyring,
            )
        elif user is None or pasw is None:
            logger.debug("Using SAM PKCE web authentication flow")
            return get_client()(
                root_url,
                debug=debug,
                strict=strict,
                use_keyring=use_keyring,
                show_login_url=show_login_url
            )
    except SystemExit:
        return


def get_client():
    return DliClient
