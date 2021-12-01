from typing import Optional

from pydantic import BaseModel


class Search(BaseModel):
    products: Optional[list]
    max_page: Optional[int]
    results: Optional[int]
    brands: Optional[list]
