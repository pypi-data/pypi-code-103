from pydantic import BaseModel
from typing import List, Dict


class ResponseBool(BaseModel):
    """布尔类型的响应"""
    message: str = "ok"
    success: bool = True


class ResponseBoolData(BaseModel):
    """布尔类型的数据响应"""
    message: str = "ok"
    success: bool = True
    data: Dict = {}


class ResponseBoolListData(BaseModel):
    """布尔类型的列表数据响应"""
    message: str = "ok"
    success: bool = True
    total: int = 0
    data: List = []
