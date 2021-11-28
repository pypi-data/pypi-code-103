import aiohttp
from . import translatorabc, translateresult, constants

# libretranslate.com hasn't implemented rate limiting yet, so you must use an alternate instance or have an API key.

class LibreTranslate(translatorabc.TranslatorABC):
    """
    LibreTranslate API, by default it'll use https://libretranslate.com/
    @endpoint_url: LibreTranslate API to use.
    """
    def __init__(self, endpoint_url: str = "https://translate.argosopentech.com/"):
        self.endpoint_url = endpoint_url

    def _parse_result(self, result: dict):
        """
        Default parser for translated result return from the server, and return a TranslateResult object.
        @result: The JSON-decoded response from the server.
        """
        translate_result = {
            "translated_text": result["translatedText"],
            "original_text": result["original_text"],
            "original_lang": result["original_lang"],
            "endpoint": self.endpoint_url,
            "raw": result
        }
        return translateresult.TranslateResult(**translate_result)

    async def translate(self, text: str, target_language: str, source_language: str = "auto", format_text: str = "text"):
        """
        Translate text from source language to target language
        @text: The text to translate.
        @target_language: The target language to translate the text into.
        @source_language: The source language of the text.
        """
        if source_language == "auto":
            source_language = await self.detect(text)

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.endpoint_url}/translate", headers = constants.LIBRETRANS_HEADER, data = {
                "q": text,
                "source": source_language,
                "target": target_language,
                "format": format_text
            }) as response:
                if response.status == 200:
                    rsp = await response.json()
                    rsp |= {
                        "original_text": text,
                        "original_lang": source_language
                    }
                    return self._parse_result(rsp)
                else:
                    raise RuntimeError("LibreTranslate returned status code {}".format(response.status))

    async def detect(self, text: str):
        """
        Detect the language of the text.
        @text: The text to detect the language.
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.endpoint_url}/detect", headers = constants.LIBRETRANS_HEADER, data = {
                "q": text
            }) as response:
                if response.status == 200:
                    return (await response.json())[0]["language"]
                else:
                    raise RuntimeError("LibreTranslate returned status code {}".format(response.status))

