from typing import TypedDict

StackParameterKey = str
# StackParameterValue = str
RegionName = str


class ApiParameter(TypedDict, total=False):
    ParameterKey: StackParameterKey
    ParameterValue: str
    ResolvedValue: str
    UsePreviousValue: bool
