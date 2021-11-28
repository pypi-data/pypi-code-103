class TranslateResult():
    """
    This class contain translation result.
    @translated_text: Translated text.
    @original_text: Original text to translate.
    @original_lang: Translated text language.
    @endpoint: Endpoint used to translate.
    @raw: Raw result returned from endpoint (sometimes deobfuscated).
    @raw_obfuscated: Raw obfuscated result returned from endpoint if @raw is deobfuscated).
    """
    def __init__(self, translated_text, original_text, original_lang, endpoint, raw, 
    raw_obfuscated = None, interjection_original = None, interjection_translated = None, original_lang_score: float = None):
        self.translated_text = translated_text
        self.original_text = original_text
        self.original_lang = original_lang
        self.original_lang_score = original_lang_score
        self.endpoint = endpoint
        self.interjection_original = interjection_original
        self.interjection_translated = interjection_translated
        self.raw = raw
        self.raw_obfuscated = raw_obfuscated
