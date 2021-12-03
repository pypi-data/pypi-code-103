"""
Annotated JSON structures as returned from TheGraph.
https://thegraph.com/hosted-service/subgraph/uniswap/uniswap-v3

For completion, consult official GraphQL schema for Uniswap 3.
https://github.com/Uniswap/v3-subgraph/blob/main/schema.graphql

Conversion is done later in the code, this is just selling what was bought :D.
"""

try:
    from typing import TypedDict
except ImportError:
    # Python <=3.7 compatibility
    from typing_extensions import TypedDict


class TokenRaw(TypedDict, total=False):
    id: str  # ETH address of the token
    symbol: str
    name: str
    derivedETH: str  # Price of the token in ethers
    decimals: str  # For some reason returned as a string
    totalSupply: str


class PoolRaw(TypedDict):
    id: str  # Returned as str from the API
    totalValueLockedETH: str
    token0Price: str
    token1Price: str
    tick: str


class TickRaw(TypedDict):
    tickIdx: str


class PositionRaw(TypedDict):
    owner: str
    token0: TokenRaw
    token1: TokenRaw
    pool: PoolRaw
    liquidity: str
    tickLower: TickRaw
    tickUpper: TickRaw
