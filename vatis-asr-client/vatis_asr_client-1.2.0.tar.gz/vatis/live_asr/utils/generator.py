from typing import Generator, Tuple, Callable
import wave

from vatis.live_asr.config.stream import StreamConfig

from vatis.live_asr.logging import get_logger


def file_generator(path: str, stream_config: StreamConfig) -> Generator[bytes, None, None]:
    """
    Creates a byte array generator the buffers the specified file.

    :param path: input file path
    :param stream_config: configuration object used to create the stream
    :return: byte array generator
    """
    CHUNK_SIZE: int = int(stream_config.sample_rate.value * stream_config.performance_config.frame_len)

    data: bytes = b''
    first_iter: bool = True

    with wave.open(path, 'rb') as wav_reader:
        while len(data) != 0 or first_iter:
            first_iter = False

            data = wav_reader.readframes(CHUNK_SIZE)

            yield data


def audio_source_generator(input_device_index, stream_config: StreamConfig, stop_condition: Callable[[int, float], bool] = None) -> Generator[bytes, None, None]:
    """
    Method for creating a byte array generator that buffers the input signal from the specified source.

    :param input_device_index: selected input device
    :param stream_config: configuration object used to create the stream
    :param stop_condition: predicate that receives the frame_count and starting_time in seconds relative to the Epoch
           and determines if the generator should stop. None means infinite streaming
    :return: byte array generator
    """
    import pyaudio
    from queue import Queue
    import time

    logger = get_logger('Input audio stream')

    audio = pyaudio.PyAudio()

    audio_format = pyaudio.get_format_from_width(stream_config.bit_depth.value)
    chunk_size: int = int(stream_config.sample_rate.value * stream_config.performance_config.frame_len)
    frame_count: int = 0
    starting_time: float = time.time()

    buffer: Queue[Tuple[bytes, int, dict]] = Queue()

    def new_audio_sample(data, samples, time_info, status_flags):
        buffer.put((data, samples, time_info))

        return data, pyaudio.paContinue

    stream = audio.open(format=audio_format, channels=stream_config.channels.value, stream_callback=new_audio_sample,
                        rate=stream_config.sample_rate.value, frames_per_buffer=chunk_size, input=True,
                        input_device_index=input_device_index)

    stream.start_stream()

    logger.info('Input audio stream started')

    stop_stream = False

    try:
        while not stop_stream:
            audio_sample: Tuple[bytes, int, dict] = buffer.get()
            frame_count += 1

            yield audio_sample[0]

            stop_stream = False if stop_condition is None else stop_condition(frame_count, starting_time)
    finally:
        stream.stop_stream()
        stream.close()

        audio.terminate()


def microphone_generator(stream_config: StreamConfig, stop_condition: Callable[[int, dict], bool] = None) -> Generator[bytes, None, None]:
    """
    Method for creating a byte array generator that buffers the input signal from the default input source (e.g. microphone).

    :param stream_config: configuration object used to create the stream
    :param stop_condition: predicate that receives the frame and time_info and determines if the generator should stop.
           None means infinite streaming
    :return: byte array generator
    """
    return audio_source_generator(input_device_index=None, stream_config=stream_config, stop_condition=stop_condition)


def print_input_devices():
    """
    Lists all the input device available
    """
    import pyaudio
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')

    for i in range(0, num_devices):
        if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
