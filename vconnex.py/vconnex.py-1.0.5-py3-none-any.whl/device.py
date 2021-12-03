"""Vconnex Device"""
from __future__ import annotations

import copy
import json
import logging
import random
import threading
import time
from abc import ABCMeta, abstractmethod
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any, NamedTuple
from urllib.parse import urlsplit

import paho.mqtt.client as mqtt

from .api import ReturnCode, VconnexAPI

LOGGER = logging.getLogger(__name__)

MQTTCLIENT_SUCCESS = 0

NOTIFY_TOPICS_KEY = "notifyTopics"
NOTIFY_TOPIC_PREFIX = "TOPIC-VCX/SmartHome-V2/Notify"
NOTIFY_NAME = "Notify"



class VconnexDevice(SimpleNamespace):
    """Vconnex Device info."""

    deviceId: str
    name: str
    status: int
    version: str
    topicContent: str
    topicNotify: str

    createdTimeStr: str
    modifiedTimeStr: str

    params: list[dict[str, Any]]

    data: dict[str, Any]

    def __init__(self, **kwargs: Any) -> None:
        """Create Vconnex Device object."""
        super().__init__(**kwargs)
        self.data = {}
        if not hasattr(self, "params") or self.params is None:
            self.params = []
        if not hasattr(self, "createdTimeStr"):
            self.createdTimeStr = None
        if not hasattr(self, "modifiedTimeStr"):
            self.modifiedTimeStr = None


class DeviceValue(NamedTuple):
    """Device value."""

    param: str
    value: Any


class DeviceMessage(SimpleNamespace):
    """Device message."""

    name: str
    devExtAddr: str
    devT: int
    batteryPercent: float
    timeStamp: int
    devV: list[dict[str, Any]]


class MqConfig(SimpleNamespace):
    """Message queue config."""

    url: str
    user: str
    password: str


class VconnexDeviceListener(metaclass=ABCMeta):
    """Device listener."""

    @abstractmethod
    def on_device_update(
        self, new_device: VconnexDevice, old_device: VconnexDevice = None
    ):
        """Update device info."""

    @abstractmethod
    def on_device_added(self, device: VconnexDevice):
        """Device Added."""

    @abstractmethod
    def on_device_removed(self, device: VconnexDevice):
        """Device removed."""


class Uninitialized(RuntimeError):
    """Error to indicate object is uninitialized."""


class ReadOnlyDict(dict):
    """Readonly Dict."""

    __readonly = False

    def readonly(self, allow=1):
        """Allow or deny modifying dictionary."""
        self.__readonly = bool(allow)

    def __setitem__(self, key, value):
        if self.__readonly:
            raise TypeError("__setitem__ is not supported")
        return dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        if self.__readonly:
            raise TypeError("__delitem__ is not supported")
        return dict.__delitem__(self, key)


class VconnexDeviceManager():
    """Device manager."""

    __initialized: bool = False

    def __init__(self, api: VconnexAPI) -> None:
        """Create Device Manager object."""
        self.__initialized = False
        self.api = api
        self.mq_client = None
        self.mq_config: dict[str, Any] = None

        self.device_map: dict[str, VconnexDevice] = {}
        self.topic_device_map: dict[str, VconnexDevice] = {}
        self.message_listeners: set[Callable[[str, str], None]] = set()
        self.device_listeners: set[VconnexDeviceListener] = set()

        self.prv_message_handler: self.MessageHanlderPrv = None
        self.prv_device_listener: self.DeviceListenerPrv = None
        self.__device_info_sync_thread: self.DeviceInfoSync = None

    def __del__(self):
        """Delete Device Manager object."""
        if self.__initialized:
            self.release()

    ###############################################################################
    ## Init
    ###############################################################################
    def __init_mq(self):
        mq_config = self.__get_mq_config()
        if mq_config is None:
            LOGGER.error("error while get mqtt config")
            return

        self.mq_config = mq_config
        mqttc = mqtt.Client(
            client_id=f"hass_client_{int(time.time() *1000)}_{random.randint(0, 1000)}",
            clean_session=False,
        )
        mqttc.username_pw_set(mq_config.user, mq_config.password)
        mqttc.user_data_set({"mq_config": mq_config})

        mqttc.on_connect = self._on_mq_connect
        mqttc.on_message = self._on_mq_message
        mqttc.on_disconnect = self._on_mq_disconnect
        mqttc.on_subscribe = self._on_mq_subscribe
        mqttc.on_log = self._on_mq_log

        url = urlsplit(mq_config.url)
        if url.scheme == "ssl":
            mqttc.tls_set()

        try:
            mqttc.connect(url.hostname, url.port, 30)

            mqttc.loop_start()
            self.mq_client = mqttc

            self.prv_message_handler = self.MessageHanlderPrv(self)
            self.prv_message_handler.start()
            self.add_message_listener(self._on_message)

        except Exception:  # pylint: disable=broad-except
            LOGGER.exception("Exception while connect mqtt client.")

    def __release_mq(self):
        mqttc = self.mq_client
        if mqttc is not None:
            if mqttc.is_connected():
                mqttc.disconnect()
            self.mq_client = None
            self.prv_message_handler.stop()
            self.prv_message_handler = None
            self.remove_message_listener(self._on_message)

    def __get_mq_config(self):
        config_dict = self._get_access_config("mqtt", "device")
        return MqConfig(**config_dict) if config_dict is not None else None

    def __init_device_map(self):
        device_list = self._get_device_list()
        if device_list is not None and len(device_list) > 0:
            device_map = {}
            for device in device_list:
                device_map[device.deviceId] = device
            self.device_map = device_map

    def __init_device(self):
        self.__init_device_map()

        self.prv_device_listener = self.DeviceListenerPrv(self)
        self.add_device_listener(self.prv_device_listener)

        for device in self.device_map.values():
            self.prv_device_listener.on_device_added(device)

        self.__device_info_sync_thread = self.DeviceInfoSync(self)
        # self.__device_info_sync_thread.start()

    def __release_device(self):
        self.device_map.clear()
        self.remove_device_listener(self.prv_device_listener)
        self.prv_device_listener = None
        self.__device_info_sync_thread.stop()
        self.__device_info_sync_thread = None

    def __check_initialize(self):
        if not self.is_initialized():
            raise Uninitialized("Object should be initital first")

    def _on_message(self, topic, message):
        LOGGER.debug("topic=%s, msg=%s", topic, message)
        self.prv_message_handler.add_message(topic, message)

    def _on_device_list_changed(self, data: Any):
        if self.__device_info_sync_thread is not None:
            self.__device_info_sync_thread.update_device_list()


    ###############################################################################
    ## Message queue callback
    ###############################################################################
    def _on_mq_connect(self, mqttc: mqtt.Client, user_data: Any, flags, rc):
        LOGGER.debug(f"connect flags->{flags}, rc->{rc}")
        if rc == 0 and self.device_map is not None:
            if self.mq_config is not None and hasattr(self.mq_config, NOTIFY_TOPICS_KEY):
                notifyTopics = list(getattr(self.mq_config, NOTIFY_TOPICS_KEY))
                for notifyTopic in notifyTopics:
                    try:
                        mqttc.subscribe(notifyTopic)
                    except: # pylint: disable=broad-except
                        LOGGER.error("Subscribe to topic=%s failure", notifyTopic)

            for device in self.device_map.values():
                if device.topicContent is not None:
                    mqttc.subscribe(device.topicContent)

        elif rc != MQTTCLIENT_SUCCESS:
            LOGGER.warning("Connect to message queue failure, attempt reconnect...")
            self.__init_mq()

    def _on_mq_disconnect(self, client: mqtt.Client, userdata: Any, rc):
        if rc != 0:
            LOGGER.error("Unexpected disconnection. code=%d", rc)
        else:
            LOGGER.debug("disconnect!")

    def _on_mq_subscribe(self, mqttc: mqtt.Client, user_data: Any, mid, granted_qos):
        LOGGER.debug("_on_subscribe: mid=%s", mid)

    def _on_mq_message(self, mqttc: mqtt.Client, user_data: Any, msg: mqtt.MQTTMessage):
        LOGGER.debug("payload-> %s", msg.payload)

        payload_str = msg.payload.decode("utf8")

        LOGGER.debug("on_message: %s", msg)

        for listener in self.message_listeners:
            listener(msg.topic, payload_str)

    def _on_mq_log(self, mqttc: mqtt.Client, user_data: Any, level, string):
        LOGGER.debug("_on_log: %s", string)

    ###############################################################################
    ###############################################################################

    def _get_access_config(self, res_type: str, res_target: str) -> dict[str, Any]:
        try:
            resp = self.api.get(
                "/access-config", {"type": res_type, "target": res_target}
            )
            if resp is not None and resp.code == ReturnCode.SUCCESS:
                return resp.data
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception("Oops, something went wrong!")
        return None

    def _get_device_list(self):
        try:
            resp = self.api.get("/devices")
            if resp is not None:
                if resp.code == ReturnCode.SUCCESS:
                    raw_list = resp.data
                    if raw_list is not None:
                        device_list = []
                        for raw in raw_list:
                            device_list.append(VconnexDevice(**raw))
                        return device_list
                elif resp.code == ReturnCode.NOT_FOUND:
                    return []
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception("Oops, something went wrong!")

        return None

    def _update_device_listener(
        self, new_device: VconnexDevice, old_device: VconnexDevice
    ):
        for listener in self.device_listeners:
            listener.on_device_update(new_device, old_device)


    ###############################################################################
    ## Public method
    ###############################################################################
    def initialize(self) -> bool:
        """Init resource."""
        try:
            self.__init_mq()
            self.__init_device()
            self.__initialized = True
            return self.__initialized
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception("Oops! Initialize failure.")
        return False

    def release(self):
        """Release resource."""
        self.__release_mq()
        self.__release_device()
        self.__initialized = False

    def is_initialized(self) -> bool:
        """Check initialized."""
        return self.__initialized

    def add_message_listener(self, listener: Callable[[str, str], None]):
        """Add message listener."""
        self.message_listeners.add(listener)

    def remove_message_listener(self, listener: Callable[[str, str], None]):
        """Remove message listener."""
        self.message_listeners.discard(listener)

    def add_device_listener(self, listener: VconnexDeviceListener):
        """Add device listener."""
        self.device_listeners.add(listener)

    def remove_device_listener(self, listener: VconnexDeviceListener):
        """Remove device listener."""
        self.device_listeners.discard(listener)

    def get_device(self, device_id: str):
        """Get device info by device id."""
        self.__check_initialize()
        return self.device_map.get(device_id, None)

    def get_device_data(self, device_id: str) -> dict[str, Any]:
        """Get device data by device id."""
        self.__check_initialize()
        if device_id in self.device_map:
            return ReadOnlyDict(self.device_map[device_id].data)
        return None

    def send_commands(self, device_id, command: str, values: dict[str, Any]) -> int:
        """Send device command."""
        self.__check_initialize()
        if device_id in self.device_map:
            try:
                body = {"deviceId": device_id, "command": command}
                body["values"] = values

                resp = self.api.post("/commands/execute", body)
                result_code = resp.code if resp is not None else ReturnCode.ERROR
                if result_code != ReturnCode.SUCCESS:
                    LOGGER.warning(
                        "Execute command [%s] of [%s] failure with code=%d",
                        command,
                        device_id,
                        result_code,
                    )
                return result_code
            except Exception:  # pylint: disable=broad-except
                LOGGER.exception("Oops, something went wrong!")
                return ReturnCode.ERROR
        else:
            LOGGER.warning("Device is not exist")
            return ReturnCode.ERROR

    class MessageHanlderPrv(threading.Thread):
        """MessageListenerPrv impl for VconnexDeviceManager."""

        def __init__(self, outer):
            """Create Device Message Handler Private object"""
            threading.Thread.__init__(self)
            self.outer = outer
            self.__running = False
            self.__queue = []

        def start(self) -> None:
            """Start threading."""
            self.__running = True
            return super().start()

        def stop(self) -> None:
            """Stop threading"""
            self.__running = False

        def add_message(self, topic: str, message: str):
            """Add device message to list"""
            self.__queue.append((topic, message))

        def handle_message(self, topic: str, message: str):
            """Handle device message."""
            try:
                msg_dict = json.loads(message)
                if "name" in msg_dict and msg_dict["name"] == NOTIFY_NAME:
                    self.__handle_notify_message(topic, msg_dict)
                else:
                    self.__handle_device_message(topic, msg_dict)
                

            except Exception:  # pylint: disable=broad-except
                LOGGER.exception("Something went wrong!!!")

        def __handle_device_message(self, topic: str, msg_dict: dict):
            if "name" in msg_dict and "devExtAddr" in msg_dict:
                device = self.outer.device_map.get(msg_dict.get("devExtAddr"))
                if device is not None:
                    msg_dict["ts"] = int(time.time() * 1000)
                    device.data[msg_dict["name"]] = msg_dict
                    self.outer._update_device_listener(device, device)
                else:
                    logging.error(
                        "Device [%s] not exists: topic=[%s], msg=[%s]",
                        msg_dict.get("devExtAddr"),
                        topic,
                        msg_dict,
                    )

        def __handle_notify_message(self, topic: str, msg_dict: dict):
            self.outer._on_device_list_changed(dict)

        def run(self) -> None:
            """Run method of threading."""
            while self.__running:
                queue_len = len(self.__queue)
                handle_queue = []
                while queue_len > 0:
                    handle_queue.append(self.__queue.pop(0))
                    queue_len = queue_len - 1

                for (topic, message) in handle_queue:
                    self.handle_message(topic, message)

                time.sleep(0.05)

    class DeviceListenerPrv(VconnexDeviceListener):
        """DeviceListener impl for VconnexDeviceManager."""

        def __init__(self, outer):
            """Create Device Message Listener Private object."""
            self.outer = outer

        def on_device_added(self, device: VconnexDevice):
            """On device added."""
            self.outer.mq_client.subscribe(device.topicContent)
            if hasattr(device, "topicNotify"):
                self.outer.mq_client.unsubscribe(device.topicNotify)

        def on_device_removed(self, device: VconnexDevice):
            """On device removed."""
            self.outer.mq_client.unsubscribe(device.topicContent)
            if hasattr(device, "topicNotify"):
                self.outer.mq_client.unsubscribe(device.topicNotify)

        def on_device_update(
            self, new_device: VconnexDevice, old_device: VconnexDevice = None
        ):
            """On device updated."""
            if old_device is None or old_device.topicContent != new_device.topicContent:
                if old_device is not None:
                    self.outer.mq_client.unsubscribe(old_device.topicContent)
                self.outer.mq_client.subscribe(new_device.topicContent)

    class DeviceInfoSync(threading.Thread):
        """Device Info Sync."""

        def __init__(self, outer) -> None:
            """Create Device Info Sync object."""
            threading.Thread.__init__(self)
            self.__running = False
            self.outer = outer

        def run(self):
            """Threading function"""
            self.__running = True
            self.__on_task_run()
        
        def stop(self):
            self.__running = False

        def __on_task_run(self):
            COUNTER_MAX = 3600 # 1h
            while self.__running:
                counter = 0
                while counter < COUNTER_MAX:
                    time.sleep(1)
                    if not self.__running:
                        break
                    counter = counter + 1
                
                if counter < COUNTER_MAX:
                    continue

                self.update_device_list

        def update_device_list(self):
            """Update device list."""
            device_list = self.outer._get_device_list()
            if device_list is None:
                return

            new_device_map = {}
            for device in device_list:
                new_device_map[device.deviceId] = device
            current_device_map = self.outer.device_map

            new_device_id_list = new_device_map.keys()
            current_device_id_list = current_device_map.keys()

            # Check removed device
            removed_device_id_list = list(
                filter(
                    lambda device_id: device_id not in new_device_id_list,
                    current_device_id_list,
                )
            )
            if len(removed_device_id_list) > 0:
                for device_id in removed_device_id_list:
                    device = current_device_map.pop(device_id)
                    for listener in self.outer.device_listeners:
                        listener.on_device_removed(device)

            # Check added device
            added_device_id_list = list(
                filter(
                    lambda device_id: device_id not in current_device_id_list,
                    new_device_id_list,
                )
            )
            if len(added_device_id_list) > 0:
                for device_id in added_device_id_list:
                    device = new_device_map.get(device_id)
                    current_device_map[device_id] = device
                    for listener in self.outer.device_listeners:
                        listener.on_device_added(device)

            # Check modified device
            modified_device_tuple_list: list[tuple[VconnexDevice, VconnexDevice]] = []
            for device_id in current_device_id_list:
                if device_id in new_device_id_list:
                    current_device = current_device_map[device_id]
                    new_device = new_device_map[device_id]
                    try:
                        if (
                            current_device.createdTimeStr != new_device.createdTimeStr
                            or current_device.modifiedTimeStr
                            != new_device.modifiedTimeStr
                        ):
                            current_device_data = current_device.data
                            old_device = copy.deepcopy(current_device)
                            for attr in vars(new_device):
                                setattr(current_device, attr, getattr(new_device, attr))
                            current_device.data = current_device_data
                            modified_device_tuple_list.append(
                                (current_device, old_device)
                            )
                    except Exception:  # py-lint: disable=broad-except
                        LOGGER.exception("Oops, something went wrong!")
            if len(modified_device_tuple_list) > 0:
                for device_tuple in modified_device_tuple_list:
                    self.outer._update_device_listener(*device_tuple)



                
