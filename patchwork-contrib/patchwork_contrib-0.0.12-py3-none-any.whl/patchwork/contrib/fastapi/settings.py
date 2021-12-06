# -*- coding: utf-8 -*-
from fastapi import FastAPI
from typing import Dict, Any, Type, Mapping, Optional

from patchwork.core.config import PublisherConfig
from pydantic import BaseModel, root_validator

from patchwork.core.typing import ClassPath

try:
    from tortoise import models
except ImportError:
    is_tortoise_installed = False
else:
    is_tortoise_installed = True

try:
    import starsessions
except ImportError:
    is_starsessions_installed = False
else:
    is_starsessions_installed = True

    class SessionsConfig(BaseModel):
        """
        Sessions configuration

        :cvar engine:
            A path to class which should be used as session backend
        :cvar data:
            Pydantic model class which represents session data model
        :cvar options:
            Options for session backend
        :cvar cookie_name:
            Name of cookie which contains session ID, by default `session_id`
        :cvar cookie_secret_key:
            A secret used to encrypt session ID
        :cvar max_age:
            Session ID cookie max age in seconds, by default 14 days
        :cvar same_site:
            Session ID cookie `same-site` option, by default `lax`
        :cvar https_only:
            Session ID cookie `https-only` option, be dafault `True`

            !!! danger
                It's strongly discouraged to set `https_only` to `False` on production deployment.
                Session ID cookie should be sent only over SSL encrypted connection to make sure that ID
                can't be stolen in the middle.
        """

        engine: ClassPath[Type[starsessions.SessionBackend]]
        data: ClassPath[Type[BaseModel]]
        options: Dict = {}
        cookie_name: str = "session_id"
        cookie_secret_key: str
        max_age: int = 14 * 24 * 60 * 60
        same_site: str = "lax"
        https_only: bool = True


class JWTConfig(BaseModel):
    """
    JWT configuration

    :cvar secret:
        A secret key for JWT encryption
    """
    secret: str


class PatchworkFastAPISettings(BaseModel):
    """
    Settings for FastAPI and Patchwork integration

    :cvar publisher:
        Optional config for publisher
    :cvar jwt:
        Optional config for JWT
    :cvar user_model:
        Optional path to user model class which must be a Tortoise ORM model
    :cvar sessions:
        Optional config for sessions
    """

    publisher: PublisherConfig = None

    jwt: JWTConfig = None

    if is_tortoise_installed:
        user_model: ClassPath[Type[models.Model]] = None
    else:
        user_model: Any = None

    if is_starsessions_installed:
        sessions: SessionsConfig = None
    else:
        sessions: Any = None

    @root_validator(pre=True)
    def check_installed_deps(cls, values):
        if 'user_model' in values:
            assert is_tortoise_installed, \
                "can't use `user_model` option without Tortoise ORM installed"
        if 'sessions' in values:
            assert is_starsessions_installed, \
                "can't use `sessions` option without Starsessions installed"

        return values


settings: PatchworkFastAPISettings


def register_patchwork(app: FastAPI, api_settings: Mapping):
    api_settings = PatchworkFastAPISettings(**api_settings)
    global settings
    settings = api_settings

    if settings.publisher is not None:
        from patchwork.contrib.fastapi import get_publisher
        publisher = get_publisher()
        app.on_event('startup')(publisher.run)
        app.on_event('shutdown')(publisher.terminate)

    if settings.sessions is not None:
        assert is_starsessions_installed, \
            "can't use sessions if starsessions lib is not installed"

        session_backend: starsessions.SessionBackend = api_settings.sessions.engine(**settings.sessions.options)

        # hijack session type until it becomes configurable in starsessions
        from .session import Session
        sdt = api_settings.sessions.data.type_
        starsessions.middleware.Session = Session[sdt].concretize(sdt)

        app.add_middleware(starsessions.SessionMiddleware,
                           secret_key=settings.sessions.cookie_secret_key,
                           session_cookie=settings.sessions.cookie_name,
                           max_age=settings.sessions.max_age,
                           same_site=settings.sessions.same_site,
                           https_only=settings.sessions.https_only,
                           backend=session_backend
                           )
