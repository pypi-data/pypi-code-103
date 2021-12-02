from typing import Optional

from vatis.live_asr.stream.observer import LiveStreamObserver, ResponseMetadata
from vatis.asr_commons.domain.transcriber import TimestampedTranscriptionPacket
from vatis.asr_commons.live.headers import FINAL_FRAME_HEADER, FRAME_START_TIME_HEADER, FRAME_END_TIME_HEADER

import sys
from io import IOBase


class LoggingLiveStreamObserver(LiveStreamObserver):
    """
    Conventional stream observer for logging events
    """
    from logging import Logger

    def __init__(self, logger: Logger = None):
        super().__init__()
        self._logger = logger

    def on_connect(self):
        message = 'Stream connected'

        if self._logger is not None:
            self._logger.info(message)
        else:
            print(message)

    def on_disconnect(self):
        message = 'Stream disconnected'

        if self._logger is not None:
            self._logger.info(message)
        else:
            print(message)

    def on_response(self, packet: TimestampedTranscriptionPacket, metadata: ResponseMetadata):
        final_frame = 'FINAL' if packet.get_header(FINAL_FRAME_HEADER, default=False) else 'PARTIAL'
        message = f'{metadata.processing_time:.2f}s {final_frame:7s} : {packet.transcript}'

        if self._logger is not None:
            self._logger.info(message)
        else:
            print(message)

    def on_close(self):
        message = 'Stream closed'

        if self._logger is not None:
            self._logger.info(message)
        else:
            print(message)

    def on_transcription_completed(self):
        message = 'Transcription completed'

        if self._logger is not None:
            self._logger.info(message)
        else:
            print(message)


class FormattedLiveStreamObserver(LiveStreamObserver):
    TEMPLATE_FINAL: str = 'FINAL\t{START:.2f} -> {END:.2f}\t{TRANSCRIPT}\n'
    TEMPLATE_PARTIAL: str = 'PARTIAL\t{START:.2f} -> {END:.2f}\t{TRANSCRIPT}\r'
    """
    Utility class for formatting and redirecting the responses to an output stream
    """
    def __init__(self, out: Optional[IOBase] = None, template_partial: str = TEMPLATE_PARTIAL,
                 template_final: str = TEMPLATE_FINAL, only_finals: bool = False):
        """
        Template placeholders:
         - FRAME_STATE: possible values are PARTIAL or FINAL
         - START: packet start time in seconds as float
         - END: packet end time in seconds as float
         - TRANSCRIPT: packet transcription

        :param out: transcript destination
        :param template_final: templated string for outputting final packages transcription
        :param template_partial: templated string for outputting partial packages transcription
        :param only_finals: flag to output only final transcription results
        """
        if out is None:
            out = sys.stdout

        self._out = out
        self._template_partial = template_partial
        self._template_final = template_final
        self._only_finals = only_finals

    def on_response(self, packet: TimestampedTranscriptionPacket, metadata: ResponseMetadata):
        if packet.get_header(FINAL_FRAME_HEADER, default=False):
            self._out.write(self._template_final.format(
                FRAME_STATE='FINAL',
                START=packet.get_header(FRAME_START_TIME_HEADER),
                END=packet.get_header(FRAME_END_TIME_HEADER),
                TRANSCRIPT=packet.transcript
            ))
        elif not self._only_finals:
            self._out.write(self._template_partial.format(
                FRAME_STATE='PARTIAL',
                START=packet.get_header(FRAME_START_TIME_HEADER),
                END=packet.get_header(FRAME_END_TIME_HEADER),
                TRANSCRIPT=packet.transcript
            ))
            self._out.flush()
