# -*- coding: utf-8 -*-
from pydantic import BaseModel


class AsyncJobEntity(BaseModel):

    """
    Unique identifier of scheduled event
    """
    event_id: str
