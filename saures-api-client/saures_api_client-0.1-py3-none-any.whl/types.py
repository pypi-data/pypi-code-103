from __future__ import annotations

import abc
import datetime
import typing

import saures_api_client.client
from saures_api_client import exceptions
from saures_api_client.misc import AsyncToSyncProxyMeta


class BaseType(metaclass=AsyncToSyncProxyMeta):
    def __repr__(self):
        items = {key: value for key, value in self.__dict__.items() if key != "client"}
        return f"{self.__class__.__name__}({items})"


class Page(BaseType):
    def __init__(self, client, object_id, number, step, count):
        self.client = client
        self.object_id = object_id
        self.number = number
        self.step = step
        self.count = count

    @property
    @abc.abstractmethod
    def client_method(self):
        pass

    async def next(self) -> Page:
        if self.count < self.number + 1:
            raise exceptions.NoPagesLeft()

        result = await self.client_method(
            self.client, object_id=self.object_id, page=self.number + 1, step=self.step
        )
        return self.__class__(
            self.client, self.object_id, result["page"], result["step"], result
        )

    async def previous(self) -> Page:
        if self.number == 1:
            raise exceptions.NoPagesLeft()

        result = await self.client_method(
            self.client, object_id=self.object_id, page=self.number - 1, step=self.step
        )
        return self.__class__(
            self.client, self.object_id, result["page"], result["step"], result
        )


class JournalPage(Page):
    def __init__(self, client, object_id, number, step, data):
        super().__init__(client, object_id, number, step, data["count"])
        self.events = data["events"]

    @property
    def client_method(self):
        return saures_api_client.client.SauresAPIClient.object_journal


class PaymentsPage(Page):
    @property
    def client_method(self):
        return saures_api_client.client.SauresAPIClient.object_payments

    def __init__(self, client, object_id, number, step, data):
        super().__init__(client, object_id, number, step, data["count"])
        self.payments = data["payments"]


class User(BaseType):
    def __init__(
        self,
        client: saures_api_client.client.SauresAPIClient,
        firstname=None,
        lastname=None,
        email=None,
        phone=None,
    ):
        self.client = client
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.phone = phone

    async def load_profile(self):
        profile = await self.client.user_profile()
        self.firstname = profile["firstname"]
        self.lastname = profile["lastname"]
        self.email = profile["email"]
        self.phone = profile["phone"]

    async def get_locations(self) -> typing.List[Location]:
        return [
            Location(self.client, **obj)
            for obj in (await self.client.user_objects())["objects"]
        ]

    @classmethod
    async def register(cls, email, firstname, lastname, phone, password) -> User:
        return await saures_api_client.client.SauresAPIClient.register_user(
            email, firstname, lastname, phone, password
        )

    @classmethod
    def login(cls, username, password):
        return saures_api_client.client.SauresAPIClient.get_user(username, password)


class Location(BaseType):
    def __init__(self, client: saures_api_client.client.SauresAPIClient, **kwargs):
        self.client = client
        self.id: int = kwargs["id"]
        self.number: str = kwargs["number"]
        self.label: str = kwargs["label"]
        self.house: str = kwargs["house"]
        self.personal_account: str = kwargs["personal_account"]
        self.enable: bool = kwargs["enable"]
        self.balance: float = kwargs["balance"]
        self.object_company_name: str = kwargs["object_company_name"]
        self.object_company_inn: str = kwargs["object_company_inn"]
        self.object_company_account: str = kwargs["object_company_account"]
        self.object_company_url: str = kwargs["object_company_url"]
        self.connect_dt: str = kwargs["connect_dt"]
        self.access_level: str = kwargs["access_level"]

    async def get_controllers(self) -> typing.List[Controller]:
        return [
            Controller(self.client, **controller_data)
            for controller_data in (await self.client.object_meters(self.id))["sensors"]
        ]

    async def get_access_info(self):
        return await self.client.object_access(self.id)

    async def get_journal(self, page=None, step=None) -> JournalPage:
        result = await self.client.object_journal(self.id, page, step)
        return JournalPage(self.client, self.id, result["page"], result["step"], result)

    async def get_payments(self, page=None, step=None) -> PaymentsPage:
        result = await self.client.object_payments(self.id, page, step)
        return PaymentsPage(
            self.client, self.id, result["page"], result["step"], result
        )

    async def get_schedules(self):
        return await self.client.object_notice(self.id)

    async def add_scheduled_push(self):
        raise NotImplementedError

    async def add_scheduled_email(self):
        raise NotImplementedError

    async def add_scheduled_mos_ru(self):
        raise NotImplementedError

    async def add_scheduled_telegram(self):
        raise NotImplementedError

    async def add_scheduled_sms(self):
        raise NotImplementedError

    async def add_scheduled_eirc(self):
        raise NotImplementedError

    async def enable_email_notifications(self):
        raise NotImplementedError

    async def enable_telegram_notifications(self):
        raise NotImplementedError

    async def enable_sms_notifications(self):
        raise NotImplementedError

    async def enable_push_notifications(self):
        raise NotImplementedError

    async def delete_notification(self):
        pass

    async def get_notifications(self):
        return await self.client.object_notice(self.id)

    async def get_schedule(self) -> typing.List[Schedule]:
        return [
            Schedule(self.client, data)
            for data in await self.client.object_schedule_get(self.id)
        ]

    @classmethod
    async def add(cls):
        raise NotImplementedError


class Controller(BaseType):
    def __init__(self, client: saures_api_client.client.SauresAPIClient, **kwargs):
        self.client = client
        self.serial_number = kwargs["sn"]
        self.name = kwargs["name"]
        self.active = kwargs["active"]
        self.ssid = kwargs["ssid"]
        self.hardware = kwargs["hardware"]
        self.firmware = kwargs["firmware"]
        self.new_firmware = kwargs["new_firmware"]
        self.battery = kwargs["bat"]
        self.local_ip = kwargs["local_ip"]
        self.check_hours = kwargs["check_hours"]
        self.check_period_display = kwargs["check_period_display"]
        self.last_connection = kwargs["last_connection"]
        self.last_connection_warning = kwargs["last_connection_warning"]
        self.lic_channels = kwargs["lic_channels"]
        self.requests = kwargs["requests"]
        self.rssi = kwargs["rssi"]
        self.log = kwargs["log"]
        self.scan = kwargs["scan"]
        self.volume = kwargs["vol"]
        self.readout_dt = kwargs["readout_dt"]
        self.request_dt = kwargs["request_dt"]
        self.cap_stat = kwargs["cap_state"]
        self.power_supply = kwargs["power_supply"]
        self.nbiot = kwargs["nbiot"]
        self.metrics = [Metric(self.client, **metric) for metric in kwargs["meters"]]
        self.available_firmwares = kwargs["available_firmwares"]

    @classmethod
    async def add(cls):
        raise NotImplementedError

    async def clear(self):
        return await self.client.sensor_clear(self.serial_number)

    async def move(self, from_location_id, to_location_id):
        return await self.client.sensor_move(
            self.serial_number, from_location_id, to_location_id
        )

    async def get_battery_history(self, start=None, finish=None):
        return await self.client.sensor_battery(
            self.serial_number, start=start, finish=finish
        )

    async def change_settings(self, name, check_hours, new_firmware=None):
        return await self.client.sensor_settings(
            self.serial_number, name, check_hours, new_firmware=new_firmware
        )

    async def delete(self):
        return self.client.sensor_delete(self.serial_number)


class Metric(BaseType):
    def __init__(self, client, **kwargs):
        self.client = client
        self.id = kwargs["meter_id"]
        self.name = kwargs["meter_name"]
        self.input = kwargs["input"]
        self.approve_dt = kwargs["approve_dt"]
        self.eirc_num = kwargs["eirc_num"]
        self.serial_number = kwargs["sn"]
        self.type = kwargs["type"]
        self.state = kwargs["state"]
        self.unit = kwargs["unit"]
        self.values = kwargs["vals"]

    async def get_history(
        self,
        start: datetime.datetime,
        finish: datetime.datetime,
        group: str,
        with_fractions: bool = True,
    ):
        return await self.client.meter_get(
            self.id, start.isoformat(), finish.isoformat(), group, not with_fractions
        )

    async def this_month_by_hours(self):
        return await self.get_history(
            datetime.datetime.now() - datetime.timedelta(days=30),
            datetime.datetime.now(),
            "hour",
        )

    async def last_30days_by_hours(self):
        return await self.get_history(
            datetime.datetime.now() - datetime.timedelta(days=30),
            datetime.datetime.now(),
            "hour",
        )

    async def this_year(self):
        pass


class Sensor(BaseType):
    def __init__(self, client):
        self.client = client

    @property
    def battery(self):
        return

    @property
    def settings(self):
        return

    @classmethod
    def add(cls):
        pass

    def move(self):
        pass

    def clear(self):
        pass

    def delete(self):
        pass


class Schedule(BaseType):
    def __init__(self, client, data):
        self.client = client
        self.month_day = data["day"]
        self.with_fractions = data["fraction"]
        self.last_dt = data["last_dt"]
        self.personal_account = data["personal_account"]
        self.resource_types = data["resource_types"]
        self.time = data["time"]
        self.type = data["type"]

    async def templates(self):
        return self.client.schedule_templates()
