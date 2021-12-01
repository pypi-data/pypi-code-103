from typing import Optional

from pydantic import BaseModel


class Option(BaseModel):
    sold: Optional[str]
    sold_url_rel: Optional[str]
