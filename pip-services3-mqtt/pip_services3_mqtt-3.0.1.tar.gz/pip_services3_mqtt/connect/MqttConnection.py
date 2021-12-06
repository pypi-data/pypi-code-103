# -*- coding: utf-8 -*-
import socket
from typing import List, Optional, Any

import paho.mqtt.client as mqtt
from pip_services3_commons.config import ConfigParams, IConfigurable
from pip_services3_commons.data import AnyValueMap
from pip_services3_commons.errors import ConnectionException, InvalidStateException
from pip_services3_commons.refer import IReferenceable, IReferences
from pip_services3_commons.run import IOpenable
from pip_services3_components.log import CompositeLogger
from pip_services3_messaging.connect.IMessageQueueConnection import IMessageQueueConnection

from pip_services3_mqtt.connect.IMqttMessageListener import IMqttMessageListener
from pip_services3_mqtt.connect.MqttConnectionResolver import MqttConnectionResolver
from pip_services3_mqtt.connect.MqttSubscription import MqttSubscription


class MqttConnection(IMessageQueueConnection, IReferenceable, IConfigurable, IOpenable):
    """
    Connection to MQTT message broker.

    MQTT is a popular light-weight protocol to communicate IoT devices.

    ### Configuration parameters ###

        - client_id:               (optional) name of the client id
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
            - retry_connect:        (optional) turns on/off automated reconnect when connection is log (default: true)
            - connect_timeout:      (optional) number of milliseconds to wait for connection (default: 30000)
            - reconnect_timeout:    (optional) number of milliseconds to wait on each reconnection attempt (default: 1000)
            - keepalive_timeout:    (optional) number of milliseconds to ping broker while inactive (default: 3000)
            
    ### References ###
        
        - `*:logger:*:*:1.0`             (optional) :class:`ICounters <pip_services3_components.log.ILogger.ILogger>` components to pass log messages
        - `*:counters:*:*:1.0`           (optional) :class:`ICounters <pip_services3_components.count.ICounters.ICounters>` components to pass collected measurements
        - `*:discovery:*:*:1.0`          (optional) :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>` services to resolve connections
        - `*:credential-store:*:*:1.0`   (optional) Credential stores to resolve credentials


    See: :class:`MessageQueue <pip_services3_mqtt.queues.MessageQueue.MessageQueue>`,
    :class:`MessagingCapabilities <pip_services3_messaging.queues.MessagingCapabilities.MessagingCapabilities>`

    """

    def __init__(self):
        """
        Creates a new instance of the connection component.
        """
        self._default_config: ConfigParams = ConfigParams.from_tuples(
            # connections. *
            # credential. *

            "client_id", None,
            "options.retry_connect", True,
            "options.connect_timeout", 30000,
            "options.reconnect_timeout", 1000,
            "options.keepalive_timeout", 60000
        )

        # The logger.
        self._logger: CompositeLogger = CompositeLogger()

        # The connection resolver.
        self._connection_resolver: MqttConnectionResolver = MqttConnectionResolver()

        # The configuration options.
        self._options: ConfigParams = ConfigParams()

        # The NATS connection pool object.
        self._connection: mqtt.Client = None

        # Topic subscriptions
        self._subscriptions: List[MqttSubscription] = []

        self._client_id: str = socket.gethostname()
        self._retry_connect: bool = True
        self._connect_timeout: int = 30000
        self._keep_alive_timeout: int = 60000
        self._reconnect_timeout: int = 1000

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        config = config.set_defaults(self._default_config)
        self._connection_resolver.configure(config)
        self._options = self._options.override(config.get_section('options'))

        self._client_id = config.get_as_string_with_default("client_id", self._client_id)
        self._retry_connect = config.get_as_boolean_with_default("options.retry_connect", self._retry_connect)
        self._connect_timeout = config.get_as_integer_with_default("options.max_reconnect", self._connect_timeout)
        self._reconnect_timeout = config.get_as_integer_with_default("options.reconnect_timeout",
                                                                     self._reconnect_timeout)
        self._keep_alive_timeout = config.get_as_integer_with_default("options.keepalive_timeout",
                                                                      self._keep_alive_timeout)

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self._logger.set_references(references)
        self._connection_resolver.set_references(references)

    def is_open(self) -> bool:
        """
        Checks if the component is opened.

        :return: true if the component has been opened and false otherwise.
        """
        return self._connection is not None

    def open(self, correlation_id: Optional[str]):
        """
        Opens the component.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if self._connection is not None:
            return

        options: AnyValueMap = self._connection_resolver.resolve(correlation_id)

        options['resubscrible'] = self._retry_connect  # TODO add params, do not support?

        try:

            def on_connect(client, user_data, flags, rc):
                if rc == 0:
                    uri = options.get('uri') or options.get('host') + str(options.get('port'))
                    self._logger.debug(correlation_id, "Connected to MQTT broker at " + uri)
                else:
                    raise ConnectionException(correlation_id, "CONNECT_FAILED",
                                              f"Connection to MQTT broker failed, return code {rc}")

            def on_message(client, userdata, msg):
                for subscription in self._subscriptions:
                    # Todo: Implement proper filtering by wildcards?
                    if subscription.filter and msg.topic != subscription.topic:
                        continue
                    subscription.listener.on_message(msg.topic, msg.payload.decode('utf-8'), msg)

            client = mqtt.Client(client_id=self._client_id)

            client.connect(
                options['host'],
                keepalive=int(self._keep_alive_timeout / 1000))

            client.on_connect = on_connect
            client.on_message = on_message
            client.reconnect_delay_set(max_delay=self._reconnect_timeout / 1000)
            client.message_retry_set(self._connect_timeout / 1000)

            client.loop_start()

            self._connection = client

        except Exception as e:
            self._logger.error(correlation_id, e, "Failed to connect to MQTT broker at " + options['uri'])
            raise ConnectionException(correlation_id, "CONNECT_FAILED",
                                      "Connection to MQTT broker failed").with_cause(e)

    def close(self, correlation_id: Optional[str]):
        if self._connection is None:
            return

        self._connection.disconnect()
        self._connection = None
        self._subscriptions = []
        self._logger.debug(correlation_id, "Disconnected from MQTT broker")

    def get_connection(self) -> Any:
        return self._connection

    def read_queue_names(self) -> List[str]:
        """
        Reads a list of registered queue names.
        If connection doesn't support this function returnes an empty list.

        - Note: Not supported

        :return: a list with registered queue names.
        """
        # Not supported
        return []

    def create_queue(self, name: str):
        """
        Creates a message queue.
        If connection doesn't support this function it exists without error.

        - Note: Not supported

        :param name: the name of the queue to be created.
        """
        # Not supported

    def delete_queue(self, name: str):
        """
        Deletes a message queue.
        If connection doesn't support this function it exists without error.

        - Note: Not supported

        :param name: the name of the queue to be deleted.
        """
        # Not supported

    def _check_open(self):
        """
        Checks if connection is open
        """
        if self.is_open(): return

        raise InvalidStateException(
            None,
            "NOT_OPEN",
            "Connection was not opened"
        )

    def publish(self, topic: str, data: Any, options: dict):
        """
        Publish a message to a specified topic

        :param topic: a topic name
        :param data: a message to be published
        :param options: publishing options
        """
        # Check for open connection
        self._check_open()

        rc, mid = self._connection.publish(topic=topic, payload=data, **options)

        if rc > 0:
            raise ConnectionException(None, "CONNECT_FAILED", mqtt.error_string(rc))

    def subscribe(self, topic: str, options: dict, listener: IMqttMessageListener):
        """
        Subscribe to a topic

        :param topic: a topic name
        :param options: subscription options
        :param listener: a message listener
        """
        # Check for open connection
        self._check_open()

        # Determine if messages shall be filtered (topic without wildcarts)
        filtered = topic.find('*') < 0

        # Add the subscription
        subscription = MqttSubscription(topic=topic,
                                        options=options,
                                        filter=filtered,
                                        listener=listener)

        self._subscriptions.append(subscription)

        # Subscribe to topic
        rc, mid = self._connection.subscribe(topic, **options)

        if rc > 0:
            del self._subscriptions[-1]
            raise ConnectionException(None, "CONNECT_FAILED", mqtt.error_string(rc))

    def unsubscribe(self, topic: str, listener: IMqttMessageListener):
        """
        Unsubscribe from a previously subscribed topic

        :param topic: a topic name
        :param listener: a message listener
        """
        # Find the subscription index
        index = -1

        for s in self._subscriptions:
            if s.topic == topic and s.listener == listener:
                index = self._subscriptions.index(s)

        if index < 0:
            return

        # Remove the subscription
        del self._subscriptions[index]

        # Check if there other subscriptions to the same topic
        index = -1
        for s in self._subscriptions:
            if s.topic == topic:
                index = self._subscriptions.index(s)

        # Unsubscribe from topic if connection is still open
        if self._connection is not None and index < 0:
            self._connection.unsubscribe(topic)
