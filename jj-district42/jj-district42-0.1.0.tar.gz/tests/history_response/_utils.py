from typing import Optional

from jj.mock import HistoryResponse
from multidict import CIMultiDict, CIMultiDictProxy

__all__ = ("make_history_response",)


def make_history_response(*,
                          status: int = 200,
                          reason: str = "OK",
                          headers: Optional[CIMultiDict] = None,
                          body: bytes = b""):
    if headers is None:
        headers = CIMultiDict()
    return HistoryResponse(
        status=status,
        reason=reason,
        headers=CIMultiDictProxy(headers),
        body=body,
    )
