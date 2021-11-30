# coding: utf-8

__all__ = [
    "RDError",
    "SessionError",
    "PlatformSessionError",
    "DesktopSessionError",
    "EndpointError",
    "StreamError",
    "StreamingError",
    "StreamConnectionError",
    "EnvError",
    "RequiredError",
    "StreamingPricesError",
    "ESGError",
    "NewsHeadlinesError",
    "BondPricingError",
    "FinancialContractsError",
    "ItemWasNotRequested",
]


class RDError(Exception):
    """Base class for exceptions in this refinitiv-data module.

    Parameters
    ----------
    code: int
        error code for this exception
    message: str
        error description for this exception
    """

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

    def __str__(self) -> str:
        return f"Error code {self.code} | {self.message}"


class SessionError(RDError):
    pass


class StreamingError(RDError):
    pass


class StreamConnectionError(RDError):
    pass


class PlatformSessionError(SessionError):
    pass


class DesktopSessionError(SessionError):
    pass


class ESGError(RDError):
    pass


class NewsHeadlinesError(RDError):
    pass


class EndpointError(RDError):
    pass


class StreamError(RDError):
    pass


class StreamingPricesError(RDError):
    pass


class ItemWasNotRequested(RDError):
    def __init__(self, item_type, not_requested, requested):
        item_type = f"{item_type}{'s' if len(not_requested) > 1 else ''}"
        super().__init__(
            -1, f"{item_type} {not_requested} was not requested : {requested}"
        )


class EnvError(RDError):
    pass


class BondPricingError(RDError):
    pass


class FinancialContractsError(RDError):
    pass


class RequiredError(RDError):
    pass
