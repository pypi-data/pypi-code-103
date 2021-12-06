# -*- coding: utf-8 -*-
from pip_services3_mqtt.connect.IMqttMessageListener import IMqttMessageListener


class MqttSubscription:

    def __init__(self, topic: str = None, filter: bool = None, options: dict = None,
                 listener: IMqttMessageListener = None):
        self.topic = topic
        self.filter = filter
        self.options = options
        self.listener = listener
