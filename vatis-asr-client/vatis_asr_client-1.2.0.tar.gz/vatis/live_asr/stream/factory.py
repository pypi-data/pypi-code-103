import socketio

from vatis.live_asr.config_variables import *
from vatis.live_asr.service import auth as auth_service
from vatis.live_asr.config.stream import StreamConfig

from vatis.asr_commons.live.headers import *
from vatis.asr_commons.live.sio_topics import *

from vatis.live_asr.logging import get_logger
from vatis.live_asr.service.auth import ClientAuthorization
from vatis.live_asr.stream.transcription import LiveStream, SimpleLiveStream, BlockingLiveStream

logger = get_logger('SIO Connection factory')


def create_stream(stream_config: StreamConfig, stream_type: str = 'BLOCKING') -> LiveStream:
    """
    Factory method for creating a LiveStream.

    :param stream_config: transcription stream configuration
    :param stream_type: stream to be created. Possible values are: SIMPLE, BLOCKING
    :return: LiveStream instance
    """
    sio = _create_sio_client(stream_config)

    if stream_type == 'SIMPLE':
        return SimpleLiveStream(sio, stream_config)
    elif stream_type == 'BLOCKING':
        return BlockingLiveStream(sio, stream_config)
    else:
        raise ValueError(f'Unsupported value {stream_type}')


def _create_sio_client(stream_config: StreamConfig) -> socketio.Client:
    sio: socketio.Client = socketio.Client(logger=DEBUG, engineio_logger=DEBUG, ssl_verify=False,
                                           request_timeout=stream_config.connection_config.request_timeout,
                                           reconnection_attempts=stream_config.connection_config.reconnection_attempts,
                                           reconnection_delay=stream_config.connection_config.reconnection_delay,
                                           reconnection=True)

    authorization: ClientAuthorization = auth_service.get_auth_token(model=stream_config.model,
                                                                     language=stream_config.language)
    auth_token: str = authorization.auth_token

    if not auth_token.startswith('Bearer'):
        auth_token = 'Bearer ' + auth_token

    service_url = f'/live/{stream_config.language.value}/transcribe'
    url = authorization.service_host + service_url

    headers = {
        'Authorization': auth_token,
        FRAME_LEN_HEADER: str(stream_config.performance_config.frame_len),
        FRAME_OVERLAP_HEADER: str(stream_config.performance_config.frame_overlap),
        BUFFER_OFFSET_HEADER: str(stream_config.performance_config.buffer_offset)
    }

    logger.debug(f'Connecting to {url} with headers {headers}')

    connection_attempts = 0

    while not sio.connected and connection_attempts < stream_config.connection_config.reconnection_attempts:
        try:
            logger.info('Connecting to ASR service. Attempt %d', connection_attempts)
            sio.connect(url=url + '/socket.io',
                        namespaces=[ASR_NAMESPACE],
                        socketio_path=service_url + '/socket.io',
                        transports=['websocket'],
                        wait=True,
                        wait_timeout=stream_config.connection_config.connection_timeout,
                        headers=headers)

            logger.info("Connection to ASR service established")
        except Exception as e:
            logger.error("Connection error", e)
            connection_attempts += 1

    if connection_attempts >= stream_config.connection_config.reconnection_attempts:
        raise ConnectionError(f'Connection to {url} failed after {connection_attempts} attempts')

    return sio
