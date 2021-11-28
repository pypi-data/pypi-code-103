"""
Another translate API for Python.
"""
from . import googletranslate, googlewebtranslate, libretranslate, bingtranslator, translateresult

__version__ = "0.2.2"
__author__ = "tretrauit"

# So we don't need to import each translation module individually
GoogleTranslate = googletranslate.GoogleTranslate
GoogleWebTranslate = googlewebtranslate.GoogleWebTranslate
LibreTranslate = libretranslate.LibreTranslate
BingTranslator = bingtranslator.BingTranslator
TranslateResult = translateresult.TranslateResult
