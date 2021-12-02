from uuid import UUID

from vatis.asr_commons.config.audio import *
from vatis.asr_commons.custom_models import Model

from vatis.live_asr.config_variables import *


class PerformanceConfig:
    """
    Performance configuration for a transcription stream. It determines how responsive the stream
    should be and how accurate the responses are
    """

    def __init__(self, frame_len: float, frame_overlap: float, buffer_offset: float):
        """
        Initialization method.
        The sum of :frame_len, :frame_overlap and :buffer_offset must be an integer number.
        General: a frame represent the samples extracted from the input signal during a period of 1 second.
        (e.g. for a signal sampled ad 16kHz, a frame is represented by 16000 consecutive samples from the signal)

        :param frame_len: Number of frames to be sent in each package.
        :param frame_overlap: Number of previously sent frames to be re-transcribed and refreshed in the transcript
        :param buffer_offset: Number of previously sent frames to be kept as a re-transcribe context.
        Those frames are not refreshed in the transcript
        """

        assert float(buffer_offset + frame_overlap + frame_len).is_integer()

        self._frame_len = frame_len
        self._frame_overlap = frame_overlap
        self._buffer_offset = buffer_offset

    @property
    def frame_len(self):
        return self._frame_len

    @property
    def frame_overlap(self):
        return self._frame_overlap

    @property
    def buffer_offset(self):
        return self._buffer_offset


SPEED_CONFIGURATION = PerformanceConfig(0.5, 1, 0.5)
ACCURACY_CONFIGURATION = PerformanceConfig(1, 2, 1)


class ConnectionConfig:
    AUTO_TIMEOUT: float = -1

    def __init__(self, reconnection_attempts: int = RECONNECTION_ATTEMPTS,
                 request_timeout: float = REQUEST_TIMEOUT, reconnection_delay: float = RECONNECTION_DELAY,
                 connection_timeout: float = CONNECTION_TIMEOUT):
        """
        :param reconnection_attempts: maximum number of initial connection or reconnection attempts
        :param request_timeout: maximum waiting time for a response from the server in seconds
        :param reconnection_delay: waiting time in seconds before performing a reconnection attempt
        :param connection_timeout: timeout for a reconnection attempt in seconds
        """
        self._reconnection_attempts = reconnection_attempts
        self._request_timeout = request_timeout
        self._reconnection_delay = reconnection_delay
        self._connection_timeout = connection_timeout

    @property
    def reconnection_attempts(self):
        return self._reconnection_delay

    @property
    def request_timeout(self):
        return self._request_timeout

    @property
    def reconnection_delay(self):
        return self._reconnection_delay

    @property
    def connection_timeout(self):
        return self._connection_timeout


DEFAULT_CONNECTION_CONFIG = ConnectionConfig()


class StreamConfig:
    """
    Configuration of the transcription stream
    """
    def __init__(self, language: Language, performance_config: PerformanceConfig = ACCURACY_CONFIGURATION,
                 connection_config: ConnectionConfig = DEFAULT_CONNECTION_CONFIG,
                 sample_rate: SampleRate = SampleRate.RATE_16000, channels: Channel = Channel.ONE,
                 bit_depth: BitDepth = BitDepth.BIT_16, model=None):
        """
        Initialization method

        :param language: language of the input signal
        :param performance_config: performance config for the stream
        :param connection_config: configuration for the connection between client and server
        :param sample_rate: signal sample rate
        :param channels: input signal sources (not implemented yet)
        :param bit_depth: audio signal bit depth
        :param model: the model used for transcription. It can be a Model object, a uid as UUID or as str
                      None means the default for the selected language
        """
        assert language is not None
        assert performance_config is not None
        assert connection_config is not None
        assert sample_rate is not None
        assert channels is not None
        assert bit_depth is not None

        self._language = language
        self._performance_config = performance_config
        self._connection_config = connection_config
        self._sample_rate = sample_rate
        self._channels = channels
        self._bit_depth = bit_depth

        if type(model) == str:
            uid: UUID = UUID(model)
            model = Model(uid=uid, language=language, name=str(uid))
        elif type(model) == UUID:
            model = Model(uid=model, language=language, name=str(model))

        self._model = model

    @property
    def performance_config(self) -> PerformanceConfig:
        return self._performance_config

    @property
    def connection_config(self) -> ConnectionConfig:
        return self._connection_config

    @property
    def language(self) -> Language:
        return self._language

    @property
    def sample_rate(self) -> SampleRate:
        return self._sample_rate

    @property
    def channels(self) -> Channel:
        return self._channels

    @property
    def bit_depth(self) -> BitDepth:
        return self._bit_depth

    @property
    def model(self) -> Model:
        return self._model
