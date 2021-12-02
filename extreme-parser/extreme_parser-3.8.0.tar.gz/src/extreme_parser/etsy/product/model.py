from typing import Optional

from pydantic import BaseModel


class Product(BaseModel):
    title: Optional[str]
    shop_id: Optional[int]
    price: Optional[float]
    favorites: Optional[int]
    stock: Optional[int]
    reviews: Optional[int]
    currency: Optional[str]
    images: Optional[list]
