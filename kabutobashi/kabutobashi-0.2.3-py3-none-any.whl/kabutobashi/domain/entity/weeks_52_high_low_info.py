from dataclasses import asdict, dataclass

from cerberus import Validator

from kabutobashi.errors import KabutobashiEntityError


@dataclass(frozen=True)
class Weeks52HighLow:
    """
    52週高値・底値の値を保持するクラス

    Args:
        code: 銘柄コード
        brand_name: 銘柄名
        close: 終値
        buy_or_sell: "買い", "強い買い", "売り", "強い売り"
        volatility_ratio: 価格変動比
        volatility_value: 価格変動値
    """

    code: int
    brand_name: str
    close: float
    buy_or_sell: str
    volatility_ratio: float
    volatility_value: float
    _SCHEMA = {
        "code": {"type": "string"},
        "brand_name": {"type": "string"},
        "close": {"type": "float"},
        "buy_or_sell": {"type": "string", "allowed": ["買い", "強い買い", "売り", "強い売り", ""]},
        "volatility_ratio": {"type": "float"},
        "volatility_value": {"type": "float"},
    }

    def __post_init__(self):
        validator = Validator(self._SCHEMA)
        if not validator.validate(self.dumps()):
            raise KabutobashiEntityError(validator)

    @staticmethod
    def from_page_of(data: dict) -> "Weeks52HighLow":
        buy = data["buy"]
        strong_buy = data["strong_buy"]
        sell = data["sell"]
        strong_sell = data["strong_sell"]

        return Weeks52HighLow(
            code=data["code"],
            brand_name=data["brand_name"],
            close=float(data["close"]),
            buy_or_sell=f"{buy}{strong_buy}{sell}{strong_sell}",
            volatility_ratio=float(Weeks52HighLow._convert(data["volatility_ratio"])),
            volatility_value=float(Weeks52HighLow._convert(data["volatility_value"])),
        )

    @staticmethod
    def _convert(input_value: str) -> str:
        if input_value == "-":
            return "0"
        return input_value.replace("%", "").replace(",", "")

    def dumps(self) -> dict:
        return asdict(self)
