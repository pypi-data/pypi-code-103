from decimal import Decimal

from thegraph_handlers._utils import safe_decimal
from thegraph_handlers.models import (
    LiquidityPoolShare,
    LiquidityPoolToken,
    LiquidityPoolUnderlyingToken,
    Token,
)
from thegraph_handlers.uniswap_v3.UNI_v3_funcs import get_amounts
from thegraph_handlers.uniswap_v3._types import (
    PositionRaw,
)


def parse_liquidity_position(raw: PositionRaw) -> LiquidityPoolShare:
    amount0, amount1 = get_amounts(
        safe_decimal(raw["pool"]["tick"]),
        safe_decimal(raw["tickLower"]["tickIdx"]),
        safe_decimal(raw["tickUpper"]["tickIdx"]),
        safe_decimal(raw["liquidity"]),
        int(raw["token0"]["decimals"]),
        int(raw["token1"]["decimals"])
    )
    amounts = [amount0, amount1]

    tokens = tuple(
        LiquidityPoolUnderlyingToken(
            token=Token(
                symbol=raw[f"token{i}"]["symbol"],
                name=raw[f"token{i}"]["name"],
                contract_address=raw[f"token{i}"]["id"],
                decimals=raw[f"token{i}"]["decimals"],
            ),
            weight=Decimal("0.5"),  # Uniswap has 1:1 ratio
            amount=amounts[i],
        )
        for i in range(2)
    )

    amount_eth = \
        tokens[0].amount * safe_decimal(raw["token0"]["derivedETH"]) \
        + tokens[1].amount * safe_decimal(raw["token1"]["derivedETH"])

    # fixme
    pool_share = (safe_decimal(raw["pool"]["totalValueLockedETH"]) * Decimal(100)) \
        / amount_eth if amount_eth != Decimal(0) else Decimal(0)

    return LiquidityPoolShare(
        user_address=raw["owner"],
        share=pool_share,
        lp_token=LiquidityPoolToken(
            token=Token(
                symbol="UNI-V3",
                name=create_lp_token_name_from_pair(raw),
                contract_address=raw["pool"]["id"],
            ),
            amount=amount_eth,
            underlying_tokens=tokens,
        ),
    )


def create_lp_token_name_from_pair(raw: PositionRaw) -> str:
    return f"Uniswap V3 - {raw['token0']['symbol']}/{raw['token1']['symbol']}"
