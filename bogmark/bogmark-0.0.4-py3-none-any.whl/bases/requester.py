import os
import pathlib
import sys
import time
import traceback
from typing import Union
from uuid import UUID

import aiohttp
import dotenv
import orjson
from aiohttp_retry import ExponentialRetry, RetryClient
from pydantic import AnyHttpUrl, Field, BaseSettings

from bogmark.logger import get_logger
from bogmark.structures.context import get_current_request_id
from bogmark.structures.response import JsonResponse

statuses_to_retry = {x for x in range(500, 600)}


class BaseAsyncRequester:
    def __init__(self, base_url=None, login=None, password=None, retries=5):
        self.load_env()
        self.base_url = base_url.rstrip("/") if base_url else self.get_base_url()
        self.service_name = os.environ["SERVICE_NAME"]
        self.logger = get_logger(__name__, type(self))
        self.login = login
        self.password = password
        self.retry_options = ExponentialRetry(attempts=retries, statuses=statuses_to_retry)

    class Config(BaseSettings):
        URL: AnyHttpUrl = Field(default="http://localhost")

    @staticmethod
    def load_env():
        for p in sys.path:
            env_path = pathlib.Path(p, "settings", ".env")
            if env_path.exists():
                dotenv.load_dotenv(env_path.as_posix())
                break

    @staticmethod
    def serialize(*args, **kwargs):
        return orjson.dumps(*args, **kwargs).decode()

    @classmethod
    def get_base_url(cls, **kwargs):
        return cls.Config().URL

    def _get_headers(self):
        return {
            "X-REQUEST-ID": get_current_request_id(),
            "X-SERVICE-NAME": self.service_name,
        }

    async def _log_request(
        self, log_level, response=None, total_time=None, before_request=False, raise_for_4xx=True, **kwargs
    ):
        log_functions = {"INFO": self.logger.info, "ERROR": self.logger.error, "WARN": self.logger.warning}
        logger = log_functions[log_level.upper()]
        cls_name = self.__class__.__name__

        if before_request:
            logger(msg=f"Sending request via {cls_name}", extra=kwargs)
            return

        msg = f"Response from {cls_name}({response.url})"
        extra = {"status_code": response.status, "url": str(response.url), "total_time": total_time}
        if response.status >= 400:
            if raise_for_4xx or 500 <= response.status < 600:
                extra.setdefault("response", {})["text"] = kwargs["resp_text"]
                logger = log_functions["ERROR"]
                msg = f"{cls_name}({response.url}) answered {response.status}"
        logger(msg=msg, extra=extra)

    @staticmethod
    def convertors(obj):
        if isinstance(obj, UUID):
            return str(obj)
        raise TypeError

    def custom_orjson_encoder(self, v):
        # orjson.dumps returns bytes, to match standard json.dumps we need to decode
        return orjson.dumps(v, default=self.convertors).decode()

    async def _make_json_request(
        self,
        method: str,
        url: str,
        headers: dict = None,
        json: Union[dict, list] = None,
        data: Union[dict, aiohttp.FormData] = None,
        params: dict = None,
        timeout=25,
        raise_for_4xx=True,
    ):
        client = RetryClient(
            retry_options=self.retry_options, logger=self.logger, json_serialize=self.custom_orjson_encoder
        )

        func_mapping = {
            "POST": client.post,
            "GET": client.get,
            "PUT": client.put,
            "DELETE": client.delete,
            "HEAD": client.head,
            "PATCH": client.patch,
        }
        send_func = func_mapping[method.upper()]
        if headers is None:
            headers = {}
        headers.update(self._get_headers())
        request_params = {
            "url": url,
            "json": json,
            "params": params,
            "headers": headers,
            "timeout": timeout,
            "data": data,
        }
        request_params = {k: v for k, v in request_params.items() if v is not None}
        if self.login and self.password:
            request_params["auth"] = aiohttp.BasicAuth(self.login, self.password)

        start_time = time.perf_counter()
        try:
            await self._log_request(before_request=True, log_level="INFO", url=request_params["url"])
            async with send_func(**request_params) as response:
                total_time = time.perf_counter() - start_time
                response_content = await response.read()
                response_text = response_content.decode()
                try:
                    response_json = orjson.loads(response_content)
                except orjson.JSONDecodeError:
                    response_json = None

                await self._log_request(
                    before_request=False,
                    log_level="INFO",
                    response=response,
                    resp_text=response_text,
                    total_time=total_time,
                    method=method.upper(),
                    raise_for_4xx=raise_for_4xx,
                )
            return JsonResponse(total_time=total_time, status_code=response.status, content=response_json)
        except Exception as e:
            self.logger.error(e, exc_info=True, extra={"stack": "".join(traceback.format_stack())})
            total_time = time.perf_counter() - start_time
            return JsonResponse(total_time=total_time, status_code=500)
        finally:
            await client.close()
