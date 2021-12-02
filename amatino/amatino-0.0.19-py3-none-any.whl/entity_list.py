"""
Amatino API Python Bindings
Entity List Module
Author: hugh@amatino.io
"""
from amatino.internal.immutable import Immutable
from amatino.internal.am_time import AmatinoTime
from amatino import User, Session, State
from typing import List, Type, TypeVar, Any, Optional
from amatino.internal.api_request import ApiRequest
from amatino.internal.url_parameters import UrlParameters
from amatino.internal.url_target import UrlTarget
from amatino.internal.http_method import HTTPMethod
from amatino.api_error import ApiError
from amatino.missing_key import MissingKey
from collections.abc import Sequence

T = TypeVar('T', bound='UserList')


class EntityList(Sequence):
    """
    An Entity List enumerates the Entities that may be accessed by the
    retreiving User.

    Amatino will return a maximum of 100 Entities per Entity List page.
    """
    _PATH = '/entities/list'

    def __init__(
        self,
        page: int,
        number_of_pages: int,
        generated_time: AmatinoTime,
        
    ) -> None: