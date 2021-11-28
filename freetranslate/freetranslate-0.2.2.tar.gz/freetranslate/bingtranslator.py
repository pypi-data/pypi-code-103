import aiohttp
import re
import json
import asyncio
from . import translatorabc, translateresult, constants

DEFAULT_ENDPOINT = "https://www.bing.com/ttranslatev3"

BING_HEADERS = constants.GOOGLE_USER_AGENT | {
    "Host": "www.bing.com",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://www.bing.com/",
    "Content-Type": "application/x-www-form-urlencoded",
    "Connection": "keep-alive"
}

class BingTranslator(translatorabc.TranslatorABC):
    """
    Bing Microsoft Translator, it'll use https://www.bing.com/ttranslatev3 as the endpoint (and https://www.bing.com/translator for the session).
    """
    def __init__(self):
        self.endpoint_url = DEFAULT_ENDPOINT
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._init())
        except RuntimeError:  # 'RuntimeError: There is no current event loop...'
            asyncio.run(self._init())
        
    # Asynchronous method to fully initialize BingTranslator
    async def _init(self):
        session_info = None
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.bing.com/translator", headers = constants.GOOGLE_USER_AGENT) as response:
                if response.status == 200:
                    self.cookies = response.cookies
                    session_info = await response.text()
                else:
                    raise RuntimeError("Bing Translator returned status code {}".format(response.status))
        try:
            # Hey Macrohard using ASP.NET for this, I'm not sure if it's the best way to do.
            self.params = {
                "IG": re.search(',IG:"\w(.+?)"', session_info).group(1),
                "IID": re.search('data-iid="\w(.+?)"', session_info).group(1)
            }
            credentials = json.loads(re.search('params_RichTranslateHelper = (.+?);', session_info).group(1))
            self.token = credentials[1]
            self.key = credentials[0]
        except Exception as e:
            raise RuntimeError(f"Failed to get Bing Translator session info,\n{e}")

    def _parse_result(self, result: dict):
        """
        Default parser for translated result return from the server, and return a TranslateResult object.
        @result: The JSON-decoded response from the server.
        """
        translation = result[0]["translations"][0]
        detected_language = result[0]["detectedLanguage"]
        translate_result = {
            "translated_text": translation["text"],
            "original_text": result[1],
            "original_lang": detected_language["language"],
            "original_lang_score": detected_language["score"],
            "endpoint": self.endpoint_url,
            "raw": result
        }
        return translateresult.TranslateResult(**translate_result)

    async def translate(self, text: str, target_language: str, source_language: str = "auto-detect"):
        """
        Translate text from source language to target language
        @text: The text to translate.
        @target_language: The target language to translate the text into.
        @source_language: The source language of the text.
        """

        data = {
            "text": text,
            "fromLang": source_language,
            "to": target_language,
            "token": self.token,
            "key": self.key
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.endpoint_url}", headers = BING_HEADERS, data = data, 
            params = self.params, cookies = self.cookies) as response:
                if response.status == 200:
                    rsp = await response.json() + [text]
                    return self._parse_result(rsp)
                else:
                    raise RuntimeError("Bing Translator returned status code {}".format(response.status))

    async def detect(self, text: str):
        """
        Detect the language of the text.
        @text: The text to detect the language.
        """
        # Think smart not work hard :))
        result = await self.translate(text, "en")
        return result.original_lang
