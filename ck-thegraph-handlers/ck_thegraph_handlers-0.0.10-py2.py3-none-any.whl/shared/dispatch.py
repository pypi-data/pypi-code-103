from typing import Any, Callable, Dict, TypedDict, Optional

from thegraph_handlers.models import Burn, LiquidityPoolShare, Mint, Swap, Token

ParserArgs = Dict[str, Any]

Data = Dict[str, Any]


class ParserDispatch(TypedDict, total=False):
    token: Optional[Callable[[Data], Token]]
    mint: Optional[Callable[[Data], Mint]]
    burn: Optional[Callable[[Data], Burn]]
    swap: Optional[Callable[[Data], Swap]]
    liquidity_position: Optional[Callable[[Data], LiquidityPoolShare]]
