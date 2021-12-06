# -*- coding: utf-8 -*-
from pip_services3_commons.refer import Descriptor
from pip_services3_messaging.build.MessageQueueFactory import MessageQueueFactory
from pip_services3_messaging.queues import IMessageQueue

from pip_services3_mqtt.queues.MqttMessageQueue import MqttMessageQueue


class MqttMessageQueueFactory(MessageQueueFactory):
    """
    Creates :class:`MqttMessageQueue <pip_services3_mqtt.queues.MqttMessageQueue.MqttMessageQueue>` components by their descriptors.
    Name of created message queue is taken from its descriptor.

    See: :class:`MqttMessageQueue <pip_services3_mqtt.queues.MqttMessageQueue.MqttMessageQueue>`,
    :class:`Factory <pip_services3_components.build.Factory.Factory>`
    """

    __MqttQueueDescriptor: Descriptor = Descriptor("pip-services", "message-queue", "mqtt", "*", "1.0")

    def __init__(self):
        """
        Create a new instance of the factory.
        """
        super().__init__()

        def factory_inner(locator: Descriptor):
            name = None if not hasattr(locator, 'get_name') else locator.get_name()
            return self.create_queue(name)

        self.register(MqttMessageQueueFactory.__MqttQueueDescriptor, factory_inner)

    def create_queue(self, name: str) -> IMessageQueue:
        """
        Creates a message queue component and assigns its name.

        :param name: a name of the created message queue.
        """
        queue = MqttMessageQueue(name)

        if self._config is not None:
            queue.configure(self._config)

        if self._references is not None:
            queue.set_references(self._references)

        return queue
