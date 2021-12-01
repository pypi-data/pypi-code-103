# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = payload_from_dict(json.loads(json_string))
#     result = envelope_from_dict(json.loads(json_string))
#     result = sample_name_date_from_dict(json.loads(json_string))
#     result = sample_y_from_dict(json.loads(json_string))
#     result = payload_t_from_dict(json.loads(json_string))
#     result = purple_t_from_dict(json.loads(json_string))
#     result = envelope_t_from_dict(json.loads(json_string))
#     result = payload_t1_from_dict(json.loads(json_string))
#     result = t1_from_dict(json.loads(json_string))

from typing import Dict, Any, List, TypeVar, Callable, Type, cast
from enum import Enum


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_dict(f: Callable[[Any], T], x: Any) -> Dict[str, T]:
    assert isinstance(x, dict)
    return { k: f(v) for (k, v) in x.items() }


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


class PayloadT:
    data: Dict[str, Any]
    kind: str

    def __init__(self, data: Dict[str, Any], kind: str) -> None:
        self.data = data
        self.kind = kind

    @staticmethod
    def from_dict(obj: Any) -> 'PayloadT':
        assert isinstance(obj, dict)
        data = from_dict(lambda x: x, obj.get("data"))
        kind = from_str(obj.get("kind"))
        return PayloadT(data, kind)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_dict(lambda x: x, self.data)
        result["kind"] = from_str(self.kind)
        return result


class PayloadT1:
    data: Dict[str, Any]
    kind: str

    def __init__(self, data: Dict[str, Any], kind: str) -> None:
        self.data = data
        self.kind = kind

    @staticmethod
    def from_dict(obj: Any) -> 'PayloadT1':
        assert isinstance(obj, dict)
        data = from_dict(lambda x: x, obj.get("data"))
        kind = from_str(obj.get("kind"))
        return PayloadT1(data, kind)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = from_dict(lambda x: x, self.data)
        result["kind"] = from_str(self.kind)
        return result


class V(Enum):
    A = "A"


class EnvelopeT:
    data: PayloadT1
    dst: List[str]
    id: str
    src: str
    t: float
    ttl: float
    v: V

    def __init__(self, data: PayloadT1, dst: List[str], id: str, src: str, t: float, ttl: float, v: V) -> None:
        self.data = data
        self.dst = dst
        self.id = id
        self.src = src
        self.t = t
        self.ttl = ttl
        self.v = v

    @staticmethod
    def from_dict(obj: Any) -> 'EnvelopeT':
        assert isinstance(obj, dict)
        data = PayloadT1.from_dict(obj.get("data"))
        dst = from_list(from_str, obj.get("dst"))
        id = from_str(obj.get("id"))
        src = from_str(obj.get("src"))
        t = from_float(obj.get("t"))
        ttl = from_float(obj.get("ttl"))
        v = V(obj.get("v"))
        return EnvelopeT(data, dst, id, src, t, ttl, v)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = to_class(PayloadT1, self.data)
        result["dst"] = from_list(from_str, self.dst)
        result["id"] = from_str(self.id)
        result["src"] = from_str(self.src)
        result["t"] = to_float(self.t)
        result["ttl"] = to_float(self.ttl)
        result["v"] = to_enum(V, self.v)
        return result


class SampleNameDate:
    date: str
    name: str

    def __init__(self, date: str, name: str) -> None:
        self.date = date
        self.name = name

    @staticmethod
    def from_dict(obj: Any) -> 'SampleNameDate':
        assert isinstance(obj, dict)
        date = from_str(obj.get("date"))
        name = from_str(obj.get("name"))
        return SampleNameDate(date, name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["date"] = from_str(self.date)
        result["name"] = from_str(self.name)
        return result


class SampleY:
    y: float

    def __init__(self, y: float) -> None:
        self.y = y

    @staticmethod
    def from_dict(obj: Any) -> 'SampleY':
        assert isinstance(obj, dict)
        y = from_float(obj.get("y"))
        return SampleY(y)

    def to_dict(self) -> dict:
        result: dict = {}
        result["y"] = to_float(self.y)
        return result


def payload_from_dict(s: Any) -> PayloadT:
    return PayloadT.from_dict(s)


def payload_to_dict(x: PayloadT) -> Any:
    return to_class(PayloadT, x)


def envelope_from_dict(s: Any) -> EnvelopeT:
    return EnvelopeT.from_dict(s)


def envelope_to_dict(x: EnvelopeT) -> Any:
    return to_class(EnvelopeT, x)


def sample_name_date_from_dict(s: Any) -> SampleNameDate:
    return SampleNameDate.from_dict(s)


def sample_name_date_to_dict(x: SampleNameDate) -> Any:
    return to_class(SampleNameDate, x)


def sample_y_from_dict(s: Any) -> SampleY:
    return SampleY.from_dict(s)


def sample_y_to_dict(x: SampleY) -> Any:
    return to_class(SampleY, x)


def payload_t_from_dict(s: Any) -> PayloadT:
    return PayloadT.from_dict(s)


def payload_t_to_dict(x: PayloadT) -> Any:
    return to_class(PayloadT, x)


def purple_t_from_dict(s: Any) -> Dict[str, Any]:
    return from_dict(lambda x: x, s)


def purple_t_to_dict(x: Dict[str, Any]) -> Any:
    return from_dict(lambda x: x, x)


def envelope_t_from_dict(s: Any) -> EnvelopeT:
    return EnvelopeT.from_dict(s)


def envelope_t_to_dict(x: EnvelopeT) -> Any:
    return to_class(EnvelopeT, x)


def payload_t1_from_dict(s: Any) -> PayloadT1:
    return PayloadT1.from_dict(s)


def payload_t1_to_dict(x: PayloadT1) -> Any:
    return to_class(PayloadT1, x)


def t1_from_dict(s: Any) -> Dict[str, Any]:
    return from_dict(lambda x: x, s)


def t1_to_dict(x: Dict[str, Any]) -> Any:
    return from_dict(lambda x: x, x)
