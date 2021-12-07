from dataclasses import dataclass, field, asdict
from typing import Optional, Any, Union, List

default = field(default='N/A')


@dataclass
class Basic:
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RequestSchema(Basic):
    url: str
    method: str = field(default='post')
    headers: Optional[dict[str, str]] = field(default=None)
    json: Any = field(default=None)
    data: Optional[dict] = field(default=None)
    params: Optional[dict] = field(default=None)
    files: Any = field(default=None)
    gql: Optional[str] = field(default=None)


@dataclass
class RequestInfoSchema(RequestSchema):
    err_msg: Optional[str] = default


@dataclass
class ResponseInfoSchema(Basic):
    code: int = field(default=500)
    time: Optional[float] = field(default=0.00)
    response: Optional[Union[dict, str]] = None
    err_msg: Optional[str] = default


@dataclass
class InterFaceInfos(Basic):
    request: Optional[RequestSchema] = None
    response: Optional[RequestInfoSchema] = None

    def __call__(self, *args, **kwargs):
        return self.to_dict()


@dataclass
class TestStep(Basic):
    request: Union[RequestSchema, 'TestCase']
    name: Optional[str] = None
    extra: Optional[dict[str, Any]] = None
    expect: Optional[dict[str, Any]] = None
    # 参数化
    arr: Optional[List[RequestSchema]] = None


@dataclass
class Config(Basic):
    # 基准地址
    base_url: Optional[str] = None
    # 基准头
    base_header: Optional[dict] = None
    # 用例名称
    name: Optional[str] = None


@dataclass
class TestCase(Basic):
    # 参数化
    config: Optional[Config] = None
    # 测试步骤
    steps: Optional[TestStep] = None




