from vatis.asr_commons.domain.transcriber import TimestampedTranscriptionPacket


class ResponseMetadata:
    def __init__(self, processing_time: int):
        self._processing_time = processing_time

    @property
    def processing_time(self) -> int:
        return self._processing_time


class LiveStreamObserver:
    def on_connect(self):
        """
        Called every time the stream connects
        """
        pass

    def on_disconnect(self):
        """
        Called every time the stream disconnects
        """
        pass

    def on_response(self, packet: TimestampedTranscriptionPacket, metadata: ResponseMetadata):
        """
        Callback for transcription response
        :param packet: the transcription response
        :param metadata: additional information about the response
        """
        pass

    def on_close(self):
        """
        Called when the stream closes and it will be no longer used
        """
        pass

    def on_transcription_completed(self):
        """
        Callback after a transcription is completed. This method will be called even if the stream was closed
        """
        pass
