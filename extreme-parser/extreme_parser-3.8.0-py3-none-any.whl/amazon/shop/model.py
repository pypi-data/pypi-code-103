from typing import Optional

from pydantic import BaseModel


class Shop(BaseModel):
    seller: Optional[str]
    name: Optional[str]
    address: Optional[str]
    stars: Optional[float]
    ratings: Optional[int]
