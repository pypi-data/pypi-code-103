from dataclasses import asdict, dataclass, field

from cerberus import Validator

from kabutobashi.errors import KabutobashiEntityError


@dataclass(frozen=True)
class StockIpo:
    """
    まだ取り込んでない値など

    '想定(仮条件)': '1,920(1,900-1,920)',
    '吸収金額': '75.6億',
    '(騰落率)損益': '(+1.1%)+2,100円00001',

    """

    code: int
    market: str = field(metadata={"jp": "市場"})
    manager: str = field(metadata={"jp": "主幹"})
    stock_listing_at: str = field(metadata={"jp": "上場日"})
    public_offering: float = field(metadata={"jp": "公募"})
    evaluation: str = field(metadata={"jp": "評価"})
    initial_price: float = field(metadata={"jp": "初値"})
    # current_price: float = field(metadata={"jp": "現在値"})
    # diff_price: float = field(metadata={"jp": "差分"})
    _SCHEMA = {
        "code": {"type": "string"},
        "market": {"type": "string"},
        "manager": {"type": "string"},
        "stock_listing_at": {"type": "string"},
        "public_offering": {"type": "float"},
        "evaluation": {"type": "string"},
        "initial_price": {"type": "float"},
    }

    def __post_init__(self):
        validator = Validator(self._SCHEMA)
        if not validator.validate(self.dumps()):
            raise KabutobashiEntityError(validator)

    @staticmethod
    def from_page_of(data: dict) -> "StockCode":
        # current_split = data["現在値(差分)"].split("(")
        return StockIpo(
            code=data["code"],
            market=data["市場"],
            manager=data["主幹"],
            stock_listing_at=data["上場"],
            public_offering=float(StockIpo._convert(data["公募"])),
            evaluation=data["評価"],
            initial_price=float(StockIpo._convert(data["初値"])),
            # current_price=0,
            # diff_price=0
        )

    @staticmethod
    def _convert(input_value: str) -> str:
        if input_value == "-":
            return "0"
        return input_value.replace("円", "").replace("株", "").replace("倍", "").replace(",", "")

    def dumps(self) -> dict:
        return asdict(self)
