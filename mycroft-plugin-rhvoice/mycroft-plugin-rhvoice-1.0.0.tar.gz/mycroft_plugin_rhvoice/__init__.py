from subprocess import run

from mycroft.configuration import Configuration
from mycroft.tts import TTS, TTSValidator


class RHVoiceTTSPlugin(TTS):
    def __init__(self, lang, config):
        super(RHVoiceTTSPlugin, self).__init__(lang, config,
                                               RHVoiceValidator(self))
        config = Configuration.get().get('tts', {}).get('rhvoice', {})
        self.voice = config.get('voice', 'aleksandr-hq')
        self.rate = int(config.get('rate', 24000))

    def get_tts(self, sentence, wav_file):
        result = run(['RHVoice-test',
                      '--output', wav_file,
                      '--profile', self.voice,
                      '--sample-rate', str(self.rate),
                      ], input=sentence, encoding='utf-8')
        if result.returncode != 0:
            self.log.error("RHVoice error: %s" % result.stderr)

        return wav_file, None


class RHVoiceValidator(TTSValidator):
    def __init__(self, tts):
        super(RHVoiceValidator, self).__init__(tts)

    def validate_lang(self):
        lang = Configuration.get().get('lang', 'en-us').split('-')[0]
        return lang in ['en', 'eo', 'ka', 'ky', 'mk', 'pt', 'ru', 'tt', 'uk']

    def validate_connection(self):
        result = run(['RHVoice-test', '--version'])
        if result.returncode != 0:
            raise Exception("RHVoice is not installed in your system.")

    def get_tts_class(self):
        return RHVoiceTTSPlugin
