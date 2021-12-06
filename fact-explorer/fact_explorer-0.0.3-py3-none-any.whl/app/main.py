from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from fact_explorer.app.db.db_session import db_instance as database_instance
from fact_explorer.app.entities.fact import FactOut
from fact_explorer.app.frontend.router import router as fe_router
from fact_explorer.config import get_configuration

from datetime import datetime, timedelta
from typing import Any, Dict, List
from json import loads, dumps
from cryptoshred.asynchronous.convenience import find_and_decrypt
from cryptoshred.backends import DynamoDbSsmBackend
from pathlib import Path

app = FastAPI()
app.mount(
    "/static",
    StaticFiles(
        directory=str(Path(__file__).resolve().parent.joinpath("frontend/static"))
    ),
    name="static",
)

app.include_router(fe_router)


@app.on_event("startup")
async def startup() -> None:
    await database_instance.connect()
    config = get_configuration()
    app.state.db = database_instance
    app.state.key_backend = DynamoDbSsmBackend(
        iv_param=config.cryptoshred_init_vector_path
    )


@app.get("/", include_in_schema=False)
async def frontend_redirect() -> RedirectResponse:
    return RedirectResponse(url="/fe/")


@app.get("/health-check")
async def health_check() -> bool:
    return True


@app.get("/api/search", response_model=List[FactOut])
async def root(
    skip: int = 0,
    limit: int = 20,
    hq: str = "{}",
    pq: str = "{}",
    decrypt: bool = False,
) -> List[Dict[str, Any]]:
    """
    Query the Facts received. Results are ordered by when the where received.
    Newest first.

    - `skip`: skip the X newest entries
    - `limit`: display X facts
    - `hq`: the header query. Use query by example here
    Just send a dict of what you are looking for.
    - `pq`: the payload query. Use query by example here.
    Just send a dict of what you are looking for.
    - `decrypt`: whether or not to decrypt cryptoshred information
    (Caution might increase response time significantly)
    """
    response = await app.state.db.fetch_by_example(
        offset=skip, limit=limit, header_example=loads(hq), payload_example=loads(pq)
    )
    result = []
    if decrypt:
        for item in response:
            decrypted = await find_and_decrypt(
                x=loads(item["payload"]), key_backend=app.state.key_backend
            )
            result.append({"header": item["header"], "payload": dumps(decrypted)})

    else:
        result = response
    return result


@app.get("/api/last", response_model=List[FactOut])
async def last(minutes: int = 15, decrypt: bool = False) -> List[Dict[str, Any]]:
    """
    Displays the Facts received in the last X minutes. Results are ordered,
    newest first.

    Beware that this is a very expensive operations in terms of memory and time.
    Use with care, you will kill the application if you use to large values.

    - `minutes`: How many minutes from now backwards you want to get.
    - `decrypt`: whether or not to decrypt cryptoshred information
    (Caution might increase response time significantly)
    """
    minutes_ago = datetime.now() - timedelta(minutes=minutes)
    response = await app.state.db.fetch_by_time(until=minutes_ago)

    result = []
    if decrypt:
        for item in response:
            decrypted = await find_and_decrypt(
                x=[item["payload"]], key_backend=app.state.key_backend
            )
            result.append({"header": item["header"], "payload": decrypted[0]})

    else:
        result = response
    return result
