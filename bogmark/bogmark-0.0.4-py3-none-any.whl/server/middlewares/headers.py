import time

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware


async def enrich_headers(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    end_time = time.perf_counter()
    response.headers["X-PROCESS-TIME"] = str(end_time - start_time)
    request_id = request.headers.get("X-REQUEST-ID")
    if request_id:
        response.headers["X-REQUEST-ID"] = request_id
    return response


def register(app: FastAPI):
    app.add_middleware(BaseHTTPMiddleware, dispatch=enrich_headers)
