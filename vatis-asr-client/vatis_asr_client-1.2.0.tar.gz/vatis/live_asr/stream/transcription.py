import base64
import json
import time
from queue import Queue
from threading import Condition
from typing import List, Generator, Callable, Optional
from threading import Thread, RLock

import socketio
from vatis.asr_commons.domain.transcriber import TimestampedTranscriptionPacket
from vatis.asr_commons.live.headers import PACKET_NUMBER_HEADER
from vatis.asr_commons.live.sio_topics import ASR_NAMESPACE, ASR_REQUEST_EVENT, ASR_RESULT_EVENT
from vatis.live_asr.stream.exception import TranscriptionError

from vatis.live_asr.config.stream import StreamConfig, ConnectionConfig
from vatis.live_asr.logging import get_logger
from vatis.live_asr.stream.observer import LiveStreamObserver, ResponseMetadata

logger = get_logger('live stream')


class LiveStream:
    WAITING_TIME_MULTIPLIER = 3

    """
    Class representing a transcription LiveStream. Each instance represents
    a different connection to the server.
    """
    def __init__(self, client: socketio.Client, config: StreamConfig):
        assert client.connected

        self._client = client
        self._config = config
        self._closed = False
        self._observers: List[LiveStreamObserver] = []
        self._last_package_sent_id = 0
        self._last_packet_received_id = 0
        self._all_packets_received: Condition = Condition()
        self._sent_timestamps = {}
        self._connected_condition = Condition()
        self._transcribing_lock = RLock()
        self._transcribing = False

        @client.event(namespace=ASR_NAMESPACE)
        def connect():
            with self._connected_condition:
                self._connected_condition.notifyAll()

            if not self._closed:
                for observer in self._observers:
                    try:
                        observer.on_connect()
                    except Exception as e:
                        logger.error('on_connected callback error', e)

        @client.event(namespace=ASR_NAMESPACE)
        def disconnect():
            self._last_package_sent_id = 0
            self._last_packet_received_id = 0

            if not self._closed:
                for observer in self._observers:
                    try:
                        observer.on_disconnect()
                    except Exception as e:
                        logger.error('on_disconnected callback error', e)

        @client.on(event=ASR_RESULT_EVENT, namespace=ASR_NAMESPACE)
        def on_message(message):
            parsed = json.loads(message)
            packet = TimestampedTranscriptionPacket(**parsed)

            self._last_packet_received_id = packet.get_header(PACKET_NUMBER_HEADER)

            metadata: ResponseMetadata = ResponseMetadata(
                processing_time=time.time() - self._sent_timestamps[self._last_packet_received_id]
            )

            self._sent_timestamps.pop(self._last_packet_received_id)

            with self._all_packets_received:
                if self._last_packet_received_id >= self._last_package_sent_id:
                    self._all_packets_received.notifyAll()

            if not self._closed:
                for observer in self._observers:
                    try:
                        observer.on_response(packet, metadata)
                    except Exception as e:
                        logger.error('on_disconnected callback error', e)

    @property
    def client(self) -> socketio.Client:
        return self._client

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def config(self) -> StreamConfig:
        return self._config

    def sid(self) -> str:
        return self._client.get_sid(namespace=ASR_NAMESPACE)

    def is_connected(self):
        return self._client.connected

    def send(self, data: bytes, received_callback=None, timeout: float = ConnectionConfig.AUTO_TIMEOUT):
        """
        Send signal frame for transcription.

        :param data: samples from the audio signal
        :param received_callback: confirmation of packet received callback
        :param timeout: waiting time in seconds to receive the transcription response for the given data frame
               once it was sent
        """
        if self._transcribing:
            raise TranscriptionError('Already transcribing')

        self._check_not_closed()

        self._feed(data, received_callback, timeout)

    def _feed(self, data: bytes, received_callback: Callable[..., None], timeout: Optional[float]):
        if timeout == ConnectionConfig.AUTO_TIMEOUT:
            timeout = self._config.performance_config.frame_len * LiveStream.WAITING_TIME_MULTIPLIER

        body = LiveStream._prepare_data(data)

        self._send_internal(body, received_callback=received_callback)

        self._last_package_sent_id += 1
        self._sent_timestamps[self._last_package_sent_id] = time.time()

        self._wait_for_completion(timeout)

    def _send_internal(self, body, received_callback):
        raise NotImplementedError('This is an abstraction method')

    @staticmethod
    def _prepare_data(data) -> dict:
        data_encoded = base64.b64encode(data)
        data_str = str(data_encoded, 'utf-8')

        return {'data': data_str}

    def _check_not_closed(self):
        if self._closed:
            raise ConnectionError('Stream disconnected')

    def add_observer(self, observer: LiveStreamObserver):
        """
        Registers a listener for stream events.

        :param observer: stream observer
        """
        self._check_not_closed()
        assert observer is not None

        self._observers.append(observer)

    def remove_observer(self, observer: LiveStreamObserver) -> bool:
        """
        Removes a stream observer

        :param observer: stream observer
        :return True if the element was deleted, False otherwise
        """
        assert observer is not None

        try:
            self._observers.remove(observer)
            return True
        except ValueError:
            return False

    def transcribe(self, data_generator: Generator[bytes, None, None], received_callback=None,
                   timeout: float = ConnectionConfig.AUTO_TIMEOUT) -> Thread:
        """
        Convenient method for transcribing a stream of data. The method is non-blocking.
        While a transcription is in process, no other transcription on this stream instance is allowed.

        :param data_generator: generator of data to be transcribed. The generated data must respect
                               the constrains specified in :send
        :param received_callback: callback for packet received by the server
        :param timeout: waiting time for processing a packet in seconds

        :return created thread
        """
        if self._transcribing:
            raise TranscriptionError('Already transcribing')

        def _transcribe():
            if self._transcribing_lock.acquire(False):
                self._transcribing = True

                try:
                    logger.info('Started transcription')

                    for data in data_generator:
                        self._feed(data, received_callback=received_callback, timeout=timeout)
                finally:
                    self._transcribing = False
                    self._transcribing_lock.release()
                    for observer in self._observers:
                        try:
                            observer.on_transcription_completed()
                        except Exception as e:
                            logger.error('on_disconnected callback error', e)
            else:
                logger.error('Already transcribing. Aborting transcription request')

        thread: Thread = Thread(target=_transcribe)
        thread.start()

        return thread

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._closed = True

        if self._client.connected:
            self._client.disconnect()

        for observer in self._observers:
            try:
                observer.on_close()
            except Exception as e:
                logger.info('on_disconnected callback error', e)

    def _wait_for_completion(self, timeout: float = None, throw: bool = False) -> bool:
        """
        Blocks the current thread until all packets sent until this method call are transcribed.

        :param timeout: timeout to wait for completion
        :return False if method timed out, True otherwise
        """
        if self._last_packet_received_id < self._last_package_sent_id:
            with self._all_packets_received:
                packet_received = self._all_packets_received.wait(timeout)
                if not packet_received and throw:
                    raise TimeoutError(f'Timed out while waiting for the packet after {timeout} seconds')

                return packet_received

    def wait_for_transcription(self, timeout: float = None):
        """
        Blocks the current thread until the current transcription in process finishes. If no transcription is in process
        the method returns immediately
        :param timeout: waiting time for transcription to finish in seconds
        """
        if timeout is None:
            timeout = -1

        if self._transcribing_lock.acquire(True, timeout):
            self._transcribing_lock.release()
        else:
            raise TimeoutError(f'Timed out while waiting for the transcription after {timeout} seconds')

    def create_generator(self) -> Generator[TimestampedTranscriptionPacket, None, None]:
        """
        Creates a generator which yields all the response packets from the stream
        :return: responses generator
        """
        responses_queue = Queue()

        class ResponseObserver(LiveStreamObserver):
            def on_response(self, packet: TimestampedTranscriptionPacket, metadata: ResponseMetadata):
                responses_queue.put(packet)

            def on_transcription_completed(self):
                responses_queue.put(None)

        observer = ResponseObserver()

        self.add_observer(observer)

        while not self._closed:
            response = responses_queue.get()

            if response is not None:
                yield response
            else:
                break

        self.remove_observer(observer)
        del responses_queue


class SimpleLiveStream(LiveStream):
    """
    Simple implementation of a live stream. It tries to send the transcription packet directly
    to the server without connection checking or retrying mechanism.
    """
    def __init__(self, client: socketio.Client, config: StreamConfig):
        super().__init__(client, config)

    def _send_internal(self, body, received_callback):
        self._client.emit(
            event=ASR_REQUEST_EVENT,
            data=body,
            namespace=ASR_NAMESPACE,
            callback=received_callback
        )


class BlockingLiveStream(LiveStream):
    """
    Live Stream implementation that blocks the :send method if the client is not currently connected until
    it's connected again or the timeout is reached.
    """
    def __init__(self, client: socketio.Client, config: StreamConfig):
        super().__init__(client, config)

    def _send_internal(self, body, received_callback):
        if not self._client.connected and not self._closed:
            connection_timeout: float = (self._config.connection_config.connection_timeout + self._config.connection_config.reconnection_delay) * \
                                         self._config.connection_config.reconnection_attempts
            with self._connected_condition:
                if not self._client.connected:
                    logger.warning(f'Client disconnected, waiting for reconnection up to {connection_timeout} seconds')
                    if not self._connected_condition.wait(connection_timeout):
                        raise TimeoutError(f'Timed out while waiting for the packet after {connection_timeout} seconds')

        self._client.emit(
            event=ASR_REQUEST_EVENT,
            data=body,
            namespace=ASR_NAMESPACE,
            callback=received_callback
        )
