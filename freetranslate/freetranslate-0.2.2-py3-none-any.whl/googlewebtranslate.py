import aiohttp
import random
import json
from . import translatorabc, translateresult, constants

class GoogleWebTranslate(translatorabc.TranslatorABC):
    """
    Google Translate API (used in https://translate.google.com), by default it'll use random API endpoint.
    @endpoint_url: Google Translate endpoint to use.
    @endpoint_urls: Google Translate endpoint list (not recommended), if `endpoint_url` is not specified then it'll use random endpoint as default.
    """
    def __init__(self, endpoint_url: str = None, endpoint_list: list() = None):
        if endpoint_list is None:
            endpoint_list = constants.GOOGLE_TRANSLATE_ENDPOINTS
        self.endpoint_list = endpoint_list
        if endpoint_url is None:
            endpoint_url = endpoint_list[random.randint(0, len(self.endpoint_list) - 1)]
        self.endpoint_url = endpoint_url
        self.RPC_ID = "MkEWBc" # Why this ID works...

    # Copied from https://github.com/ssut/py-googletrans/pull/255/files
    def _build_rpc_request(self, text: str, dest: str, src: str):
        return json.dumps([[
            [
                self.RPC_ID,
                json.dumps([[text, src, dest, True],[None]], separators=(',', ':')),
                None,
                'generic',
            ],
        ]], separators=(',', ':'))

    # Get random endpoints
    def _get_endpoint(self):
        self.endpoint_list[random.randint(0, len(self.endpoint_list) - 1)]

    # Copied from https://github.com/ssut/py-googletrans/pull/255/files with some minimal optimization
    def _parse_result(self, result: str, source_language: str = "auto"):
        """
        Default parser for translated result return from the server, and return a TranslateResult object.
        @result: The fucked JSON response from the server (Good JSON obfuscator there Google ;))
        """
        token_found = False
        square_bracket_counts = [0, 0]
        resp = ''
        for line in result.split("\n"):
            token_found = token_found or f'"{self.RPC_ID}"' in line[:30]

            if not token_found:
                continue

            is_in_string = False
            for i, v in enumerate(line):
                if v == '\"' and line[max(0, i - 1)] != '\\':
                    is_in_string = not is_in_string
                if not is_in_string:
                    if v == '[':
                        square_bracket_counts[0] += 1
                    elif v == ']':
                        square_bracket_counts[1] += 1

            resp += line
            if square_bracket_counts[0] == square_bracket_counts[1]:
                break

        parsed = json.loads(json.loads(resp)[0][2])

        # After decoding using py-googletrans decoder, we get the following JSON like
        # [[None, None, 'vi', [[[0, [[[None, 8]], [True]]]], 8]], [[[None, None, None, True, None, [['Hi', None, None, None, [['Hi', [2]], ['Hello', [2, 5]]]]]]], 'en', 1, 'vi', ['Xin chào', 'auto', 'en', True]], 'vi', ['Xin chào!', None, None, None, None, [[['interjection', [['Hello!', None, ['Alô!', 'Chào anh!', 'Chào chị!', 'Ô nài!', 'Xin chào!'], 1, True]], 'en', 'vi']], 1], None, None, 'vi', 1]]
        # (use https://jsonformatter.curiousconcept.com/ to format it)
        # Then we can try to manually parse it like me below .-.

        #interjection_original = set()
        #interjection_translated = None
        #for v in parsed[3][6][0][0][1][0]:
        #    if isinstance(v, str):
        #        interjection_original.add(v)
        #    elif isinstance(v, list):
        #        interjection_translated = v
        #        break
        original_lang = parsed[0][2]
        if original_lang is None:
            original_lang = source_language

        translate_result = {
            "translated_text": parsed[1][0][0][5][0][0], # What the hell is this
            "original_text": parsed[1][4][0],
            #"interjection_original": list(interjection_original),
            #"interjection_translated": interjection_translated,
            "original_lang": original_lang,
            "endpoint": self.endpoint_url,
            "raw": parsed, # We don't want to give people a mess
            "raw_obfuscated": result # Enjoy hell :(
        }
        return translateresult.TranslateResult(**translate_result)

    # Copied from https://github.com/ssut/py-googletrans/pull/255/files
    async def translate(self, text: str, target_language: str, source_language: str = "auto"):
        """
        Translate text from source language to target language
        @text: The text to translate.
        @target_language: The target language to translate the text into.
        @source_language: The source language of the text.
        """
        data = {
            'f.req': self._build_rpc_request(text, target_language, source_language),
        }
        params = {
            'rpcids': self.RPC_ID,
            'bl': 'boq_translate-webserver_20201207.13_p0',
            'soc-app': 1,
            'soc-platform': 1,
            'soc-device': 1,
            'rt': 'c',
        }
        # Patched headers
        headers = constants.GOOGLE_USER_AGENT | {'Referer': 'https://translate.google.com'}

        async with aiohttp.ClientSession() as session:
            async with session.post("https://{host}/_/TranslateWebserverUi/data/batchexecute".format(host=self.endpoint_url), 
            params=params, data=data, headers=headers) as response:
                if response.status == 200:
                    return self._parse_result(await response.text())
                else:
                    raise RuntimeError("Google Web Translate returned status code {}".format(response.status))

    async def detect(self, text: str):
        """
        Detect the language of the text.
        @text: The text to detect the language.
        """
        # Think smart not work hard :))
        result = await self.translate(text, "en")
        return result.original_lang
