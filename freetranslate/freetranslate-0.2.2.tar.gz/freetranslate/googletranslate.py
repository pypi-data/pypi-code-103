import aiohttp
import random
from . import translatorabc, translateresult, constants

# https://github.com/ssut/py-googletrans/issues/268#issue-777566195
DEFAULT_ENDPOINTS = ["https://clients5.google.com/translate_a/t?client=dict-chrome-ex"] 

class GoogleTranslate(translatorabc.TranslatorABC):
    """
    Google Translate API, by default it'll use random API endpoint.
    @endpoint_url: Google Translate API to use.
    @endpoint_urls: Google Translate API list (not recommended), if `endpoint_url` is not specified then it'll use random API endpoint as default.
    """
    def __init__(self, endpoint_url: str = None, endpoint_list: list() = None):
        if endpoint_list is None:
            self._get_default_endpoints()
            endpoint_list = DEFAULT_ENDPOINTS
        self.endpoint_list = endpoint_list
        if endpoint_url is None:
            endpoint_url = endpoint_list[random.randint(0, len(DEFAULT_ENDPOINTS) - 1)]
        self.endpoint_url = endpoint_url

    def _get_default_endpoints(self):
        """
        Get default endpoints defined in the module.
        return set: The default endpoints.
        """
        for endpoint in constants.GOOGLE_TRANSLATE_ENDPOINTS:
            endpoint_url = f"https://{endpoint}/translate_a/single?client=gtx&dt=t"
            if endpoint_url not in DEFAULT_ENDPOINTS:
                DEFAULT_ENDPOINTS.append(endpoint_url)
        return DEFAULT_ENDPOINTS # For convenience, I won't use it btw.

    def _parse_result(self, result: dict):
        """
        Default parser for translated result return from the server, and return a TranslateResult object.
        @result: The JSON-decoded response from the server.
        """
        translate_result = {}
        try:
            translate_result |= {
                "translated_text": result[0][0][0],
                "original_text": result[0][0][1],
                "original_lang": result[2],
                "raw": result
            }
        except (KeyError, TypeError):
            # Use legacy Chrome Translate extension decoder
            sentence = result["sentences"][0]
            translate_result |= {
                "translated_text": sentence["trans"],
                "original_text": sentence["orig"],
                "original_lang": sentence["orig"],
                "raw": result
            }
        translate_result |= {
            "endpoint": self.endpoint_url,
        }
        return translateresult.TranslateResult(**translate_result)

    async def translate(self, text: str, target_language: str, source_language: str = "auto"):
        """
        Translate text from source language to target language
        @text: The text to translate.
        @target_language: The target language to translate the text into.
        @source_language: The source language of the text.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(self.endpoint_url, params = {
                "q": text,
                "sl": source_language,
                "tl": target_language
            }, headers=constants.GOOGLE_USER_AGENT) as response:
                if response.status == 200:
                    return self._parse_result(await response.json())
                else:
                    raise RuntimeError("Google Translate returned status code {}".format(response.status))

    async def detect(self, text: str):
        """
        Detect the language of the text.
        @text: The text to detect the language.
        """
        # Think smart not work hard :))
        result = await self.translate(text, "en")
        return result.original_lang
