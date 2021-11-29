from typing import Dict

from ai_api_client_sdk.helpers.authenticator import Authenticator


def form_top_skip_params(top: int = None, skip: int = None) -> Dict[str, int]:
    """
    Frame query param

    :param top: Number of objects to be retrieved, defaults to None
    :type top: int, optional
    :param skip: Number of objects to be skipped, from the list of the queried objects,
        defaults to None
    :type skip: int, optional
    """
    params = {}
    if top:
        params['$top'] = top
    if skip:
        params['$skip'] = skip
    if not params:
        params = None
    return params
