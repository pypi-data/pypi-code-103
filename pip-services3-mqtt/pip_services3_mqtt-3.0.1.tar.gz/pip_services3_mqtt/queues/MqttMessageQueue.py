# -*- coding: utf-8 -*-
import datetime
import json
import time
from typing import List, Optional, Any

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.errors import ConnectionException, InvalidStateException
from pip_services3_commons.refer import IUnreferenceable, IReferences, DependencyResolver
from pip_services3_commons.run import IOpenable, ICleanable
from pip_services3_components.log import CompositeLogger
from pip_services3_messaging.queues import MessageQueue, MessagingCapabilities, MessageEnvelope, IMessageReceiver

from pip_services3_mqtt.connect.MqttConnection import MqttConnection


class MqttMessageQueue(MessageQueue, IUnreferenceable, IOpenable, ICleanable):
    """
    Message queue that sends and receives messages via MQTT message broker.

    MQTT is a popular light-weight protocol to communicate IoT devices.

    ### Configuration parameters ###

        - topic:                         name of MQTT topic to subscribe
        - connection(s):
            - discovery_key:               (optional) a key to retrieve the connection from :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>`
            - host:                        host name or IP address
            - port:                        port number
            - uri:                         resource URI or connection string with all parameters in it
        - credential(s):
            - store_key:                   (optional) a key to retrieve the credentials from :class:`ICredentialStore <pip_services3_components.auth.ICredentialStore.ICredentialStore>`
            - username:                    user name
            - password:                    user password
        - options:
            - serialize_envelope:   (optional) true to serialize entire message as JSON, false to send only message payload (default: true)
            - autosubscribe:        (optional) true to automatically subscribe on option (default: false)
            - qos:                  (optional) quality of service level aka QOS (default: 0)
            - retain:               (optional) retention flag for published messages (default: false)
            - retry_connect:        (optional) turns on/off automated reconnect when connection is log (default: true)
            - connect_timeout:      (optional) number of milliseconds to wait for connection (default: 30000)
            - reconnect_timeout:    (optional) number of milliseconds to wait on each reconnection attempt (default: 1000)
            - keepalive_timeout:    (optional) number of milliseconds to ping broker while inactive (default: 3000)

    ### References ###

        - *:logger:*:*:1.0              (optional) :class:`ILogger <pip_services3_components.log.ILogger.ILogger>` components to pass log messages
        - *:counters:*:*:1.0            (optional) :class:`ICounters <pip_services3_components.count.ICounters.ICounters>` components to pass collected measurements
        - *:discovery:*:*:1.0           (optional) :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>` services to resolve connections
        - *:credential-store:*:*:1.0    (optional) Credential stores to resolve credentials
        - *:connection:mqtt:*:1.0       (optional) Shared connection to MQTT service

    See: :class:`MessageQueue <pip_services3_mqtt.queues.MessageQueue.MessageQueue>`,
    :class:`MessagingCapabilities <pip_services3_messaging.queues.MessagingCapabilities.MessagingCapabilities>`

    Example:

    .. code-block:: python

        queue = MqttMessageQueue("myqueue")

        queue.configure(ConfigParams.from_tuples(
            "topic", "mytopic",
            'connection.protocol', 'mqtt',
            "connection.host", "localhost",
            "connection.port", 1883
        ))

        queue.open("123")
        queue.send("123", MessageEnvelope(None, "mymessage", "ABC"))
        message = queue.receive("123", 10000)
    """
    _default_config: ConfigParams = ConfigParams.from_tuples(
        "topic", None,
        "options.serialize_envelope", False,
        "options.autosubscribe", False,
        "options.retry_connect", True,
        "options.connect_timeout", 30000,
        "options.reconnect_timeout", 1000,
        "options.keepalive_timeout", 60000,
        "options.qos", 0,
        "options.retain", False
    )

    def __init__(self, name: str = None):
        """
        Creates a new instance of the persistence component.

        :param name: (optional) a queue name.
        """
        super().__init__(name, MessagingCapabilities(False, True, True, True, True, False, False, False, True))

        self.__config: ConfigParams = None
        self.__references: IReferences = None
        self.__opened: bool = False
        self.__local_connection: bool = None

        # The dependency resolver.
        self._dependency_resolver: DependencyResolver = DependencyResolver(MqttMessageQueue._default_config)

        # The logger.
        self._logger: CompositeLogger = CompositeLogger()

        # The MQTT connection component.
        self._connection: MqttConnection = None

        self._serialize_envelope: bool = None
        self._topic: str = None
        self._qos: int = None
        self._retain: bool = None
        self._auto_subscribe: bool = None
        self._subscribed: bool = None
        self._messages: List[MessageEnvelope] = []
        self._receiver: IMessageReceiver = None

    def configure(self, config: ConfigParams):
        """
        Configures object by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        config = config.set_defaults(MqttMessageQueue._default_config)
        self.__config = config

        self._dependency_resolver.configure(config)

        self._topic = config.get_as_string_with_default("topic", self._topic)
        self._auto_subscribe = config.get_as_boolean_with_default("options.autosubscribe", self._auto_subscribe)
        self._serialize_envelope = config.get_as_boolean_with_default("options.serialize_envelope",
                                                                      self._serialize_envelope)
        self._qos = config.get_as_integer_with_default("options.qos", self._qos)
        self._retain = config.get_as_boolean_with_default("options.retain", self._retain)

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self.__references = references
        self._logger.set_references(references)

        # Get connection
        self._dependency_resolver.set_references(references)
        self._connection = self._dependency_resolver.get_one_optional('connection')
        # Or create a local one
        if self._connection is None:
            self._connection = self.__create_connection()
            self.__local_connection = True
        else:
            self.__local_connection = False

    def unset_references(self):
        """
        Unsets (clears) previously set references to dependent components.
        """
        self._connection = None

    def __create_connection(self) -> MqttConnection:
        connection = MqttConnection()

        if self.__config:
            connection.configure(self.__config)

        if self.__references:
            connection.set_references(self.__references)

        return connection

    def is_open(self) -> bool:
        """
        Checks if the component is opened.

        :return: true if the component has been opened and false otherwise.
        """
        return self.__opened

    def open(self, correlation_id: Optional[str]):
        """
        Opens the component.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if self.__opened:
            return

        if self._connection is None:
            self._connection = self.__create_connection()
            self.__local_connection = True

        if self.__local_connection is not None:
            self._connection.open(correlation_id)

        if not self._connection.is_open():
            raise ConnectionException(
                correlation_id,
                "CONNECT_FAILED",
                "MQTT connection is not opened"
            )

        # Subscribe right away
        if self._auto_subscribe:
            self._subscribe(correlation_id)

        self.__opened = True

    def close(self, correlation_id: Optional[str]):
        """
        Closes component and frees used resources.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if not self.__opened:
            return

        if self._connection is None:
            raise InvalidStateException(
                correlation_id,
                'NO_CONNECTION',
                'MQTT connection is missing'
            )

        if self.__local_connection:
            self._connection.close(correlation_id)

        if self._subscribed:
            # Unsubscribe from the topic
            topic = self._get_topic()
            self._connection.unsubscribe(topic, self)

        self._messages = []
        self.__opened = False
        self._receiver = None

    def _get_topic(self) -> str:
        return self._topic if self._topic is not None and self._topic != '' else self.get_name()

    def _subscribe(self, correlation_id: Optional[str]):
        if self._subscribed:
            return

        # Subscribe right away
        topic = self._get_topic()

        self._connection.subscribe(topic, {'qos': self._qos}, self)

    def _from_message(self, message: MessageEnvelope) -> Optional[dict]:
        if message is None: return None

        data = message.message

        if self._serialize_envelope:
            message.sent_time = datetime.datetime.now()
            data = json.dumps(message.to_json())

        return {
            'topic': self._topic if self.get_name() == 'undefined' and self._topic else self.get_name(),
            'data': data
        }

    def _to_message(self, topic: str, data: Any, packet: Any) -> Optional[MessageEnvelope]:
        if data is None: return

        message: MessageEnvelope

        if self._serialize_envelope:
            message = MessageEnvelope.from_json(data)
        else:
            message = MessageEnvelope(None, topic, data)
            message.message_id = packet.message_id
            # message.message_type = topic
            # message.message = data

        return message

    def on_message(self, topic: str, data: Any, packet: Any):
        # Skip if it came from a wrong topic
        expected_topic = self._get_topic()
        if expected_topic.find('*') < 0 and expected_topic != topic:
            return

        # Deserialize message
        message = self._to_message(topic, data, packet)
        if message is None:
            self._logger.error(None, None, "Failed to read received message")
            return

        self._counters.increment_one("queue." + self.get_name() + ".received_messages")
        self._logger.debug(message.correlation_id, "Received message %s via %s", message, self.get_name())

        # Send message to receiver if its set or put it into the queue
        if self._receiver is not None:
            self.__send_message_to_receiver(self._receiver, message)
        else:
            self._messages.append(message)

    def clear(self, correlation_id: Optional[str]):
        """
        Clears component state.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        self._messages = []

    def read_message_count(self) -> int:
        """
        Reads the current number of messages in the queue to be delivered.

        :return: number of available messages.
        """
        return len(self._messages)

    def peek(self, correlation_id: Optional[str]) -> MessageEnvelope:
        """
        Peeks a single incoming message from the queue without removing it.
        If there are no messages available in the queue it returns None.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :return: a peeked message.
        """
        self._check_open(correlation_id)

        # Subscribe to topic if needed
        message = None
        if len(self._messages) > 0:
            message = self._messages[0]

        if message is not None:
            self._logger.trace(message.correlation_id, "Peeked message %s on %s", message, self.get_name())

        return message

    def peek_batch(self, correlation_id: Optional[str], message_count: int) -> List[MessageEnvelope]:
        """
        Peeks multiple incoming messages from the queue without removing them.
        If there are no messages available in the queue it returns an empty list.

        Important: This method is not supported by MQTT.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param message_count: a maximum number of messages to peek.
        :return: a list with peeked messages.
        """
        self._check_open(correlation_id)

        # Subscribe to topic if needed
        self._subscribe(correlation_id)

        # Peek a batch of messages
        messages = self._messages[: message_count]

        self._logger.trace(correlation_id, "Peeked %d messages on %s", len(messages), self.get_name())

        return messages

    def receive(self, correlation_id: Optional[str], wait_timeout: int) -> MessageEnvelope:
        """
        Receives an incoming message and removes it from the queue.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param wait_timeout: a timeout in milliseconds to wait for a message to come.
        :return: a received message.
        """
        self._check_open(correlation_id)

        # Subscribe to topic if needed
        self._subscribe(correlation_id)

        message = None

        # Return message immediately if it exist
        if len(self._messages) > 0:
            message = self._messages.pop(0)
            return message

        # Otherwise wait and return
        check_interval = 100
        elapsed_time = 0

        while True:
            test = self.is_open() and elapsed_time < wait_timeout and message is None
            if not test: break
            time.sleep(check_interval / 1000)
            message = None if len(self._messages) < 1 else self._messages.pop(0)
            elapsed_time += check_interval

        return message

    def send(self, correlation_id: Optional[str], message: MessageEnvelope):
        """
        Sends a message into the queue.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param message: a message envelop to be sent.
        """
        self._check_open(correlation_id)

        self._counters.increment_one("queue." + self.get_name() + ".sent_messages")
        self._logger.debug(message.correlation_id, "Sent message %s via %s", message.to_json(), self.to_string())

        msg = self._from_message(message)
        options = {'qos': self._qos, 'retain': self._retain}
        self._connection.publish(msg['topic'], msg['data'], options)

    def renew_lock(self, message: MessageEnvelope, lock_timeout: int):
        """
        Renews a lock on a message that makes it invisible from other receivers in the queue.
        This method is usually used to extend the message processing time.

        Important: This method is not supported by MQTT.

        :param message: a message to extend its lock.
        :param lock_timeout: a locking timeout in milliseconds.
        """
        # Not supported

    def complete(self, message: MessageEnvelope):
        """
        Permanently removes a message from the queue.
        This method is usually used to remove the message after successful processing.

        Important: This method is not supported by MQTT.

        :param message: a message to remove.
        """
        # Not supported

    def abandon(self, message: MessageEnvelope):
        """
        Returnes message into the queue and makes it available for all subscribers to receive it again.
        This method is usually used to return a message which could not be processed at the moment
        to repeat the attempt. Messages that cause unrecoverable errors shall be removed permanently
        or/and send to dead letter queue.

        Important: This method is not supported by MQTT.

        :param message: a message to return.
        """
        # Not supported

    def move_to_dead_letter(self, message: MessageEnvelope):
        """
        Permanently removes a message from the queue and sends it to dead letter queue.

        Important: This method is not supported by MQTT.

        :param message: a message to be removed.
        """
        # Not supported

    def __send_message_to_receiver(self, receiver: IMessageReceiver, message: MessageEnvelope):
        correlation_id = None if message is None else message.correlation_id
        if message is None or receiver is None:
            self._logger.warn(correlation_id, "MQTT message was skipped.")
            return

        try:
            self._receiver.receive_message(message, self)
        except Exception as e:
            self._logger.error(correlation_id, e, "Failed to process the message")

    def listen(self, correlation_id: Optional[str], receiver: IMessageReceiver):
        """
        Listens for incoming messages and blocks the current thread until queue is closed.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param receiver: a receiver to receive incoming messages.
        """
        self._check_open(correlation_id)

        # Subscribe to topic if needed
        self._subscribe(correlation_id)
        # timeout for subscribe
        time.sleep(0.01)

        self._logger.trace(None, "Started listening messages at %s", self.get_name())

        # Resend collected messages to receiver
        while self.is_open() and len(self._messages) > 0:
            message = self._messages.pop(0)
            if message is not None:
                self.__send_message_to_receiver(receiver, message)

        # Set the receiver
        if self.is_open():
            self._receiver = receiver

    def end_listen(self, correlation_id: Optional[str]):
        """
        Ends listening for incoming messages.
        When this method is call `listen` unblocks the thread and execution continues.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        self._receiver = None
