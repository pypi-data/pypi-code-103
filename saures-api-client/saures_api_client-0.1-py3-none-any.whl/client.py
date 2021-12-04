import asyncio
import functools

from aiohttp import ClientOSError, ClientSession

import saures_api_client.types
from saures_api_client import constants, exceptions
from saures_api_client.constants import GET, POST


class RequestsLimiter:
    def __init__(self, f):
        self.count = 1
        self.f = f

    async def release(self):
        await asyncio.sleep(60)
        self.count -= 1

    async def __call__(self, *args, **kwargs):
        while self.count > constants.REQUESTS_PER_MINUTE_MAX:
            await asyncio.sleep(0.5)
        result = await self.f(*args, **kwargs)
        self.count += 1
        asyncio.create_task(self.release())
        return result


def apply_limits(func):
    @functools.wraps(func)
    async def wrapped(client, *args, **kwargs):
        for _ in range(constants.RETRIES_COUNT):
            try:
                return await func(client, *args, **kwargs)
            except ClientOSError:
                await asyncio.sleep(constants.SLEEP_BETWEEN_RETRIES)
        raise exceptions.RetryLimitExceeded()

    return wrapped


def drop_none(data: dict):
    for key, value in data.copy().items():
        if value is None:
            data.pop(key)
    return data


class SauresAPIClient:
    def __init__(self, email, password, api_url=constants.API_URL):
        self.email = email
        self.password = password
        self.api_url = api_url
        self.sid = None

    @apply_limits
    @RequestsLimiter
    async def _send_request(self, method, endpoint, **kwargs):
        print(method, endpoint, kwargs)
        async with ClientSession() as session:
            async with session.request(
                method, f"{self.api_url}/{endpoint}", **kwargs
            ) as request:
                response = await request.json()

        print(response)
        if response["status"] == "ok":
            return response["data"]
        if response["errors"]:
            for error in response["errors"]:
                exception = getattr(exceptions, error["name"])
                if exception is not None:
                    raise exception(error.get("msg", "No message provided"))

    async def authenticate(self):
        params = {"email": self.email, "password": self.password}
        response = await self._send_request(POST, "login", data=params)
        self.sid = response["sid"]

    async def _make_request(self, method, endpoint, params=None):
        if self.sid is None:
            await self.authenticate()

        params = params or {}
        params.update({"sid": self.sid})

        kwargs = {}
        if method == GET:
            kwargs["params"] = drop_none(params)
        else:
            kwargs["data"] = drop_none(params)

        return await self._send_request(method, endpoint, **kwargs)

    @classmethod
    def get_user(cls, email, password) -> saures_api_client.types.User:
        return saures_api_client.types.User(cls(email, password))

    async def user_profile(self):
        return await self._make_request(GET, "user/profile")

    async def user_objects(
        self,
    ):
        return await self._make_request(GET, "user/objects")

    async def object_meters(self, object_id, date=None):
        return await self._make_request(
            GET, "object/meters", {"id": object_id, "date": date}
        )

    async def meter_get(self, meter_id, start, finish, group, absolute):
        return await self._make_request(
            GET,
            "meter/get",
            {
                "id": meter_id,
                "start": start,
                "finish": finish,
                "group": group,
                "absolute": int(bool(absolute)),
            },
        )

    async def meter_control(self, meter_id, command):
        return await self._make_request(
            POST, "meter/control", {"id": meter_id, "command": command}
        )

    async def object_access(self, object_id):
        return await self._make_request(GET, "object/access", {"id": object_id})

    async def object_journal(self, object_id, page, step):
        return await self._make_request(
            GET,
            "object/journal",
            {
                "id": object_id,
                "page": page,
                "step": step,
            },
        )

    async def object_notice(self, object_id):
        return await self._make_request(
            GET,
            "object/notice",
            {
                "id": object_id,
            },
        )

    async def object_payments(self, object_id, page, step):
        return await self._make_request(
            GET,
            "object/payments",
            {
                "id": object_id,
                "page": page,
                "step": step,
            },
        )

    async def sensor_battery(self, serial_number, start, finish):
        return await self._make_request(
            GET,
            "sensor/battery",
            {
                "sn": serial_number,
                "start": start,
                "finish": finish,
            },
        )

    async def sensor_move(self, serial_number, from_object, to_object):
        return await self._make_request(
            GET,
            "sensor/move",
            {
                "sn": serial_number,
                "from": from_object,
                "to": to_object,
            },
        )

    async def sensor_clear(self, serial_number):
        return await self._make_request(
            GET,
            "sensor/clear",
            {
                "sn": serial_number,
            },
        )

    async def sensor_settings(
        self, serial_number, name, check_hours, new_firmware=None
    ):
        return await self._make_request(
            POST,
            "sensor/settings",
            drop_none(
                {
                    "sn": serial_number,
                    "name": name,
                    "check_hours": check_hours,
                    "new_firmware": new_firmware,
                }
            ),
        )

    async def sensor_delete(self, serial_number):
        return await self._make_request(
            POST,
            "sensor/delete",
            {
                "sn": serial_number,
            },
        )

    async def object_schedule_get(self, object_id):
        return await self._make_request(GET, "object/schedule", {"id": object_id})

    async def object_schedule_post(self):
        return await self._make_request(POST, "object/schedule")

    async def schedule_templates(self):
        return await self._make_request(GET, "schedule/templates")

    @classmethod
    async def register_user(cls, email, firstname, lastname, phone, password):
        return
