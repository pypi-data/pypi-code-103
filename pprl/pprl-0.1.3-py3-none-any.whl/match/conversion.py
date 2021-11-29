from typing import Dict

from .model import MatchConfig, MatchRequest, Match


def serialize_match_config(config: MatchConfig) -> Dict:
    """
    Converts a match configuration object into a dictionary.

    :param config: Match configuration to convert
    :return: Converted match configuration
    """
    return {
        "match-function": config.match_function,
        "selection-strategy": config.selection_strategy,
        "threshold": str(config.threshold),
        "match-mode": config.match_mode
    }


def serialize_bit_vector(bit_vector: str) -> Dict:
    """
    Converts a bit vector into a dictionary.

    :param bit_vector: Bit vector to convert
    :return: Converted bit vector
    """
    return {
        "bit-vector": bit_vector
    }


def serialize_match_request(request: MatchRequest) -> Dict:
    """
    Converts a match request into a dictionary.

    :param request: Match request object to convert
    :return: Converted match request
    """
    return {
        "domain-entity-list": [
            serialize_bit_vector(d) for d in request.domain_bit_vectors
        ],
        "range-entity-list": [
            serialize_bit_vector(r) for r in request.range_bit_vectors
        ],
        "match-configuration": serialize_match_config(request.match_config),
    }


def deserialize_match(d: Dict) -> Match:
    """
    Converts a match dictionary into a match object.

    :param d: Dictionary to convert
    :return: Converted dictionary
    """
    return Match(
        domain_bit_vector=d["domain-bit-vector"],
        range_bit_vector=d["range-bit-vector"],
        confidence=d["confidence"]
    )
