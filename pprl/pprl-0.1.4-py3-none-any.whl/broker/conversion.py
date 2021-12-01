from typing import Dict

from .model import SessionCancellation, SessionRequest, BrokerMatch
from ..match.conversion import serialize_match_config


def serialize_session_cancellation(cancel: SessionCancellation) -> Dict:
    """
    Converts a session cancellation object into a dictionary.

    :param cancel: Object to convert
    :return: Converted session cancellation
    """
    d = {"method": cancel.method}

    for k, v in cancel.options.items():
        d[str(k)] = str(v)

    return d


def serialize_session_request(request: SessionRequest) -> Dict:
    """
    Converts a session request object into a dictionary.

    :param request: Object to convert
    :return: Converted session request
    """
    return {
        "match-configuration": serialize_match_config(request.match_config),
        "session-cancellation": serialize_session_cancellation(request.session_cancellation)
    }


def deserialize_match(d: Dict) -> BrokerMatch:
    """
    Converts a dictionary into a match object.

    :param d: Dictionary to convert
    :return: Converted dictionary
    """
    return BrokerMatch(d["bit-vector"], d["confidence"])


def deserialize_secret_response(d: Dict) -> str:
    """
    Extracts a secret from a dictionary.

    :param d: Dictionary to extract secret from
    :return: Extracted secret
    """
    return d["secret"]