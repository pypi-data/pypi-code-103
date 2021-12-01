import json
import logging
import os
from pathlib import Path
from typing import Union

GRID_URL = os.getenv("GRID_URL", 'https://platform.grid.ai')

TERMINAL_STATES = {"CANCELLED", "FAILED", "SUCCEEDED"}
STARTED_STATES = {"RUNNING", *TERMINAL_STATES}
WAITING_STATES = {"PENDING"}

IGNORE_WARNINGS = None

logger = logging.getLogger(__name__)  # pragma: no cover

DEBUG = os.getenv("DEBUG")

SKIP_VERSION_CHECK = bool(os.getenv('GRID_SKIP_VERSION_CHECK'))

CONTEXT = os.getenv('GRID_CONTEXT_CLUSTER_ID')

SHOW_PROCESS_STATUS_DETAILS = os.getenv('SHOW_PROCESS_STATUS_DETAILS')

GRID_SKIP_GITHUB_TOKEN_CHECK = bool(os.getenv("GRID_SKIP_GITHUB_TOKEN_CHECK", default=None))

TESTING = os.getenv("TESTING", default=os.getenv("CI", default=None))

SSL_CA_CERT = os.getenv("REQUESTS_CA_BUNDLE", default=os.getenv("SSL_CERT_FILE", default=None))

GRID_SSH_CONFIG = os.getenv("GRID_SSH_CONFIG", default=str(Path.home() / ".ssh/config"))


def _load_global_settings(grid_settings_path: Union[str, Path], set_context_if_not_exists=True) -> None:
    """`=
    Loads user settings and sets them globally
    in the Client context.

    Parameters
    ----------
    set_context_if_not_exists:
        Set the context information if it doesn't exist. This is True always except on requests like login
    """
    global DEBUG, SKIP_VERSION_CHECK, CONTEXT, IGNORE_WARNINGS

    from grid.sdk import list_clusters

    P = Path.home().joinpath(grid_settings_path)
    # Make sure path exists.
    Path(P.parents[0]).mkdir(parents=True, exist_ok=True)
    # If file doesn't exist, create with default global settings
    if not P.exists():
        global_variables = {'debug': False, 'ignore_warnings': False, 'skip_vesion_check': False}
        with P.open('w') as file:
            json.dump(global_variables, file, ensure_ascii=False, indent=4)

    # adding context to the user settings
    user_settings = json.load(P.open())
    if set_context_if_not_exists and 'context' not in user_settings:
        cluster_list = list_clusters(is_global=True)
        default_cluster = cluster_list.default_cluster
        user_settings['context'] = default_cluster
        with P.open('w') as file:
            json.dump(user_settings, file, ensure_ascii=False, indent=4)

    if 'debug' in user_settings and DEBUG is None:
        DEBUG = bool(user_settings['debug'])

    if 'ignore_warnings' in user_settings and IGNORE_WARNINGS is None:
        IGNORE_WARNINGS = bool(user_settings['ignore_warnings'])

    if 'skip_version_check' in user_settings and SKIP_VERSION_CHECK is None:
        SKIP_VERSION_CHECK = bool(user_settings['skip_vesion_check'])

    if 'context' in user_settings and CONTEXT is None:
        CONTEXT = user_settings['context']
