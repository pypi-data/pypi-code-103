import logging

from urllib3 import PoolManager
from urllib3.exceptions import TimeoutError

logger = logging.getLogger(__name__)


def hello():
    return "Hola soy load!!!"


def download_sound(sound):
    http = PoolManager()
    url = f"https://www.google.com/search?q={sound}&tbm=isch"
    try:
        response = http.request("GET", url)
        logger.error("Download successfull")
    except TimeoutError:
        logger.error("Timeout")

    return response
