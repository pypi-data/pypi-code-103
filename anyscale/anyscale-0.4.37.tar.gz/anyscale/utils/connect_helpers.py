from dataclasses import dataclass
import inspect
from typing import Any


try:
    from ray.client_builder import ClientContext
except ImportError:
    # Import error will be raised in `ClientBuilder.__init__`.
    # Not raising error here to allow `anyscale.connect required_ray_version`
    # to work.
    @dataclass
    class ClientContext:  # type: ignore
        pass


@dataclass
class AnyscaleClientConnectResponse:
    """
    Additional information returned about clusters that were connected from Anyscale.
    """

    cluster_id: str


class AnyscaleClientContext(ClientContext):  # type: ignore
    def __init__(
        self, anyscale_cluster_info: AnyscaleClientConnectResponse, **kwargs: Any,
    ) -> None:
        if _multiclient_supported() and "_context_to_restore" not in kwargs:
            # Set to None for now until multiclient is supported on connect
            kwargs["_context_to_restore"] = None
        super().__init__(**kwargs)
        self.anyscale_cluster_info = anyscale_cluster_info


def _multiclient_supported() -> bool:
    """True if ray version supports multiple clients, False otherwise"""
    _context_params = inspect.signature(ClientContext.__init__).parameters
    return "_context_to_restore" in _context_params
