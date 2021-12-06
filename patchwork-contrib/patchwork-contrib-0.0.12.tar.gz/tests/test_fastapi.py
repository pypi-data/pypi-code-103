# -*- coding: utf-8 -*-

import pytest
from pydantic import BaseModel
from starsessions import InMemoryBackend

from patchwork.contrib.fastapi.session import Session


class SessionData(BaseModel):
    foo: str = ""


@pytest.mark.asyncio
async def test_session_usage():

    backend = InMemoryBackend()
    session_t = Session[SessionData].concretize(SessionData)
    session = session_t(backend=backend)
    assert not session.is_loaded

    await session.load()
    session.data.foo = "bar"
    assert session.is_modified

    id = await session.persist()
    loaded_session = session_t(backend, id)
    await loaded_session.load()

    assert loaded_session.is_loaded
    assert loaded_session.data.foo == "bar"
