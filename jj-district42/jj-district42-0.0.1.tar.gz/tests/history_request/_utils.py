from typing import Dict, Optional

from jj.mock import HistoryRequest
from multidict import CIMultiDict, CIMultiDictProxy, MultiDict, MultiDictProxy

__all__ = ("make_history_request",)


def make_history_request(*,
                         method: str = "GET",
                         path: str = "/",
                         segments: Optional[Dict[str, str]] = None,
                         params: Optional[MultiDict] = None,
                         headers: Optional[CIMultiDict] = None,
                         body: bytes = b""):
    if segments is None:
        segments = {}
    if params is None:
        params = MultiDict()
    if headers is None:
        headers = CIMultiDict()

    return HistoryRequest(
        method=method,
        path=path,
        segments=segments,
        params=MultiDictProxy(params),
        headers=CIMultiDictProxy(headers),
        body=body,
    )
