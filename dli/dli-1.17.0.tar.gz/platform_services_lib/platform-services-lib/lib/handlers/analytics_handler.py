import queue
import threading
from typing import Callable, Optional
from urllib.parse import urljoin

import requests

from ..context.urls import consumption_urls
from abc import ABC


class AnalyticsSender(ABC, threading.Thread):

    BUFFER_THRESHOLD = 10

    def __init__(self, config, session_func: Optional[Callable[[], requests.Session]]):
        self.__session_func = session_func
        super().__init__()
        self.setDaemon(True)
        self.config = config
        self.queue = queue.Queue()
        self._buffer = []
        self.start()

    def run(self):
        while True:
            # Send buffer every 5 seconds
            try:
                event = self.queue.get(block=True, timeout=5)
                if event is None:
                    # end thread
                    break

                self._buffer.append(event)

                if len(self._buffer) > self.BUFFER_THRESHOLD:
                    self._send_buffer()
            except queue.Empty:
                # Means we've timed out.
                # send what's in the buffer
                self._send_buffer()
                continue

    def _send_buffer(self, timeout: float = 5):
        """
        Send any queued analytics events to our analytics backend in a single request. If there is any problem with
        sending then we are keeping the code simple and dropping the event (many endpoints on the backend also trigger
        analytics).

        :param float timeout: Default 5. How long to wait for the server to send data before giving up. If this is
            too low (e.g. 0.1) then we give up before the connection is established! 0.5 works in a VirtualBox VM, but
            we have seen some users on slow networks (either because they are in a different regions or because of
            firewalls) so we can set this value high as it happens in a background thread. 5 was chosen to match the
            polling time for the analytics queue.
        """
        try:
            if len(self._buffer):
                url = urljoin(
                    self.config.get('consumption_env'),
                    consumption_urls.consumption_analytics
                )
                if self.__session_func:
                    # Use a function to get the session. The session cannot be passed by reference as it will need to
                    # be refreshed automatically when it expires.
                    session = self.__session_func()
                    # Check session exists, as we do not have a session before the `dli.connect` has been called.
                    if session:
                        session.post(url, json={'data': self._buffer}, timeout=timeout)
                self._buffer = []

        except Exception as e:
            # Data scientists do not want to see stack dumps by default,
            # especially when we have a root cause that triggers secondary
            # exceptions.
            if self.config.get('strict') and self.config.get('logger'):
                logger = self.config.get('logger')
                logger.exception(
                    'Error while sending analytics: ', e
                )


class AnalyticsHandler:
    __acceptable_properties = [
        'package_id', 'dataset_id', 'name', 'dataset_name', 'datafile_id',
        'dictionary_id', 'api_key'
    ]

    def __init__(self, analytics_sender: AnalyticsSender):
        self._analytics_sender = analytics_sender

    def create_event(
        self, user_id, organisation_id,
        entity=None, action=None, properties=None, result_status_code=None
    ):
        body = self._prepare_body_to_send(
            user_id, organisation_id, entity, action, properties,
            result_status_code,
        )
        self._send_event_to_analytics(body)

    def _prepare_body_to_send(
        self, user_id, organisation_id, entity, action, properties, result
    ):
        properties_to_send = self._filter_out_properties(properties)
        properties_to_send = self._override_properties_for_dataset_functions(
            action, entity, properties, properties_to_send)

        event = {
            'application_name': self._analytics_sender.config.get('app_name', 'Unknown'),
            'application_version': self._analytics_sender.config.get('version', 'Unknown'),
            'user_id': user_id,
            'entity': entity,
            'action': action,
            'organisation_id': organisation_id,
            'result': result,
            'properties': properties_to_send
        }
        return {'attributes': event}

    def _filter_out_properties(self, properties):
        return {
            k: v
            for k, v in properties.items() if k in self.__acceptable_properties
        }

    # This is ugly, but 1) register_dataset accepts builder,
    # so we need to extract data from it 2) some functions accept 'id'
    # instead of dataset_id. We either ovveride it like this or not make it
    # generic at all.
    def _override_properties_for_dataset_functions(
            self, action, entity, properties, props
    ):
        if entity == 'Dataset':
            if action == 'register_dataset':
                props = self._filter_out_properties(properties['builder']._data)
            elif 'id' in properties:
                props['dataset_id'] = properties['id']
        return props

    def __del__(self):
        # tell the queue it's over
        self._analytics_sender.queue.put(None)

    def _send_event_to_analytics(self, body):
        # if not os.environ.get('DEV_MODE', 'False').lower() == 'true':
        self._analytics_sender.queue.put(body)