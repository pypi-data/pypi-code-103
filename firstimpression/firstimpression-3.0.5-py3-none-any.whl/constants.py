import mimetypes
import re

mimetypes.init()

PICTURE_FORMATS = {
    'fullscreen': "http://narrowcasting.fimpweb.nl/imageresize.php?width=1920&url=",
    'square':     "http://narrowcasting.fimpweb.nl/imageresize.php?width=512&url=",
}


APIS = {
    'amber': 'AMBER_ALERT',
    'schiphol': 'AMS_AIRPORT',
    'bbc': 'BBC',
    'ns': 'NS',
    'traffic': 'TRAFFIC',
    'insta': 'INSTAGRAM',
    'weather': 'WEATHER',
    'jokes': 'CHUCK_NORRIS',
    'eindhoven': 'EHV_AIRPORT',
    'facebook': 'FACEBOOK',
    'trends': 'GOOGLE_TRENDS',
    'news_polish': 'INTERIA',
    'concerts': 'SONGKICK',
    'nu': 'NU',
    'solaredge': 'SOLAREDGE',
    'countdown': 'COUNTDOWN',
    'twitter': 'TWITTER',
    'world_times': 'WORLD_TIMES',
    'default': 'DEFAULT'
}

VIDEO_EXTENSIONS = [
    ext for ext in mimetypes.types_map if mimetypes.types_map[ext].split('/')[0] == 'video']
IMG_EXTENSIONS = [
    ext for ext in mimetypes.types_map if mimetypes.types_map[ext].split('/')[0] == 'image']

ENGLISH_INDEX = 0
DUTCH_INDEX = 1


TAGS_TO_REMOVE = re.compile(r'<[^>]+>')
REPLACE_DICT = {
    "<em>": "<italic = \"On\">",
    "</em>": "<italic = \"Off\">",
    "<b>": "<bold = \"On\">",
    "</b>": "<bold = \"Off\">",
    u'\xa0': ""
}

CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

LEVELNAME = {
    CRITICAL: 'CRITICAL',
    ERROR: 'ERROR',
    WARNING: 'WARNING',
    INFO: 'INFO',
    DEBUG: 'DEBUG',
    NOTSET: 'NOTSET',
}
NAMELEVEL = {
    'CRITICAL': CRITICAL,
    'FATAL': FATAL,
    'ERROR': ERROR,
    'WARN': WARNING,
    'WARNING': WARNING,
    'INFO': INFO,
    'DEBUG': DEBUG,
    'NOTSET': NOTSET,
}

SAMSUNG_MONITOR_ON_MESSAGE = b'\xAA\x11\xFE\x01\x01\x11'
SAMSUNG_MONITOR_OFF_MESSAGE = b'\xAA\x11\xFE\x01\x00\x10'
SAMSUNG_MONITOR_SWITCH_PORT = 1515
