# -*- coding: utf-8 -*-
from typing import Union

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from patchwork.core import AsyncPublisher
from starlette import status
from starlette.requests import Request

from .settings import is_tortoise_installed, is_starsessions_installed


class PublisherWrapper:

    def __init__(self):
        self._publisher = None

    def __call__(self) -> AsyncPublisher:
        from .settings import settings
        if settings.publisher is None:
            raise RuntimeError("unable to use publisher as it's not configured")

        if self._publisher is None:
            self._publisher = settings.publisher.instantiate()
        return self._publisher


get_publisher = PublisherWrapper()


if is_starsessions_installed:
    from starsessions import Session

    async def current_session(request: Request):
        ss: Session = request.session
        await ss.load()
        return ss
else:
    async def current_session(*args, **kwargs):
        raise RuntimeError('no supported sessions backend')


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def _get_user_id(token) -> int:
    from .settings import settings
    payload = jwt.decode(token, settings.jwt.secret, algorithms=["HS256"])
    user_id: int = int(payload.get("sub"))
    return user_id


async def current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        return _get_user_id(token)
    except (JWTError, TypeError):
        raise credentials_exception


async def optional_current_user_id(token: str = Depends(oauth2_scheme)) -> Union[int, None]:
    try:
        return _get_user_id(token)
    except (JWTError, TypeError):
        return None


if is_tortoise_installed:
    from tortoise.exceptions import DoesNotExist

    async def current_user(cuid: int = Depends(current_user_id)):
        from .settings import settings
        try:
            return await settings.user_model.type_.get(user_id=cuid)
        except DoesNotExist:
            raise credentials_exception

    async def optional_current_user(cuid: Union[int, None] = Depends(optional_current_user_id)):
        if cuid is None:
            return None

        from .settings import settings
        try:
            return await settings.user_model.type_.get(user_id=cuid)
        except DoesNotExist:
            return None

else:
    async def current_user(*args, **kwargs):
        raise RuntimeError('no supported ORM installed')

    async def optional_current_user(*args, **kwargs):
        raise RuntimeError('no supported ORM installed')
