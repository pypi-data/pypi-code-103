from typing import Tuple
import requests

# Set the version of the library here
__version__ = "0.6.2"


class ServerCheckError(Exception):
    pass


def get_server_version(server_url: str) -> Tuple[str, str]:
    """Function to fetch the discover endpoint from the local server

    Returns:
        a dict with the version and build hash
    """
    try:
        resp = requests.get(f"{server_url}/core/v1/discover")
        if resp.status_code != 200:
            raise ServerCheckError(f"Failed to load version information from server. Status Code: {resp.status_code}")
    except requests.exceptions.ConnectionError:
        raise ServerCheckError(f"Failed to load version information from server. Could not connect to server.")

    data = resp.json()

    return data['version'], data['build']
