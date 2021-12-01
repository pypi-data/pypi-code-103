from typing import Dict

from .model import ClientConfig, ResolveRequest, PseudonymMatch
from ..encoder.conversion import serialize_encoder_config


def serialize_client_config(config: ClientConfig) -> Dict:
    """
    Converts a client config into a dictionary.

    :param config: Client config to convert
    :return: Converted client config
    """
    return {
        "domain": config.domain,
        "attributes": config.attributes
    }


def serialize_resolve_request(request: ResolveRequest) -> Dict:
    """
    Converts a request to resolve pseudonyms into a dictionary.

    :param request: Resolve request to convert
    :return: Converted resolve request
    """
    return {
        "client-config": serialize_client_config(request.client_config),
        "encoder-config": serialize_encoder_config(request.encoder_config),
        "pseudonyms": request.pseudonyms
    }


def deserialize_pseudonym_match(d: Dict) -> PseudonymMatch:
    """
    Converts a dictionary into a pseudonym match object.

    :param d: Dictionary to convert
    :return: Converted dictionary
    """
    return PseudonymMatch(d["pseudonym"], d["confidence"])
