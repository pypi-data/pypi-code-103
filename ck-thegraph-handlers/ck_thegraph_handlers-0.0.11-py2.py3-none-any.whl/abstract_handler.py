import abc
from collections import AsyncGenerator

from thegraph_handlers._protocols import AClosableHTTPClient
from thegraph_handlers.models import LiquidityPoolShare
from thegraph_handlers.shared.dispatch import ParserDispatch


class AbstractHandler(abc.ABC):

    @abc.abstractmethod
    def __init__(
        self,
        client: AClosableHTTPClient,
    ) -> None:
        pass

    @abc.abstractmethod
    async def yield_liquidity_pool_shares(
        self, address: str, include_withdrawn: bool = False
    ) -> AsyncGenerator[LiquidityPoolShare, None]:
        raise NotImplementedError
