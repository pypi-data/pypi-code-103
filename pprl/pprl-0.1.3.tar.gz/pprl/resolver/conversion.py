from typing import Dict

from .model import MPIConfig, ResolveRequest, PseudonymMatch
from ..encoder.conversion import serialize_encoder_config


def serialize_mpi_config(config: MPIConfig) -> Dict:
    """
    Converts an MPI configuration into a dictionary.

    :param config: MPI configuration to convert
    :return: Converted MPI configuration
    """
    return {
        "domain": config.domain,
        "pseudonyms": [pseudonym for pseudonym in config.pseudonyms]
    }


def serialize_resolve_request(request: ResolveRequest) -> Dict:
    """
    Converts a request to resolve pseudonyms into a dictionary.

    :param request: Resolve request to convert
    :return: Converted resolve request
    """
    return {
        "mpi-configuration": serialize_mpi_config(request.mpi_config),
        "encoder-configuration": serialize_encoder_config(request.encoder_config),
        "attribute-list": request.attribute_list
    }


def deserialize_pseudonym_match(d: Dict) -> PseudonymMatch:
    """
    Converts a dictionary into a pseudonym match object.

    :param d: Dictionary to convert
    :return: Converted dictionary
    """
    return PseudonymMatch(d["pseudonym"], d["confidence"])
