"""System Wide Constants for pymeteobridgedata."""
from __future__ import annotations

BASE_URL = "https://api.weatherbit.io/v2.0"

ALERT_ADVISORY = "Advisory"
ALERT_WATCH = "Watch"
ALERT_WARNING = "Warning"

CONDITION_CLASSES = {
    "partlycloudy-night": [8010, 8020],
    "clear-night": [8000],
    "cloudy": [803, 804],
    "exceptional": [900],
    "fog": [700, 711, 721, 731, 741, 751],
    "hail": [623],
    "lightning": [230, 231, 232, 233],
    "lightning-rainy": [200, 201, 202],
    "partlycloudy": [801, 802],
    "pouring": [502, 522],
    "rainy": [300, 301, 302, 500, 501, 511, 520, 521, 522],
    "snowy": [600, 601, 602, 621, 622, 623],
    "snowy-rainy": [610, 611, 612],
    "sunny": [800],
    "windy": [],
    "windy-variant": [],
}

DATA_TYPES = [
    "current",
    "forecast",
    "alert",
]

LANGUAGE_EN = "en"
VALID_LANGUAGES = [
    LANGUAGE_EN,
    "ar",
    "az",
    "be",
    "bg",
    "bs",
    "ca",
    "cz",
    "da",
    "de",
    "fi",
    "fr",
    "el",
    "es",
    "ja",
    "hr",
    "hu",
    "id",
    "it",
    "is",
    "iw",
    "kw",
    "lt",
    "nb",
    "nl",
    "pl",
    "pt",
    "ro",
    "ru",
    "sk",
    "sl",
    "sr",
    "sv",
    "tr",
    "uk",
    "zh",
    "zh-tw",

]

DEFAULT_TIMEOUT = 10

UNIT_TYPE_METRIC = "metric"
UNIT_TYPE_IMPERIAL = "imperial"

VALID_UNIT_TYPES = [
    UNIT_TYPE_IMPERIAL,
    UNIT_TYPE_METRIC,
]

WEATHER_ALERTS = [
    ALERT_ADVISORY,
    ALERT_WATCH,
    ALERT_WARNING
]
