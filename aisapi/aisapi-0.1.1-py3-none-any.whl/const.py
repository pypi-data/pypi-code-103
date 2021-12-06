"""Constants."""

AIS_WS_TUNE_IN_URL = "http://opml.radiotime.com/"
AIS_WS_AUDIO_TYPE_URL = (
    "https://powiedz.co/ords/dom/dom/audio_type?nature={audio_nature}"
)
AIS_WS_AUDIO_NAME_URL = (
    "https://powiedz.co/ords/dom/dom/audio_name?nature={audio_nature}&type={audio_type}"
)
AIS_WS_AUDIOBOOKS_URL = "https://wolnelektury.pl/api/audiobooks/?format=json"
AIS_WS_AUDIO_INFO = "https://powiedz.co/ords/dom/dom/get_audio_full_info"
AIS_WS_COMMAND_URL = "{ais_url}/command"
AIS_WS_AUDIO_STATUS_URL = "{ais_url}/audio_status"
AIS_WS_TTS_URL = "{ais_url}/text_to_speech?text={text}"
